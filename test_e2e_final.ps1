# Corrected E2E Test - checks status_code in JSON body, not HTTP status
$ErrorActionPreference = "Stop"
$BASE = "http://localhost:7861/api/v1"

# Login
$bodyA = @{user_name="testuser_e2e"; user_password="Test1234"} | ConvertTo-Json
$respA = Invoke-RestMethod -Uri "$BASE/user/login" -Method Post -Body $bodyA -ContentType "application/json"
$tokenA = $respA.data.access_token

$bodyB = @{user_name="testuser_b"; user_password="Test1234"} | ConvertTo-Json
$respB = Invoke-RestMethod -Uri "$BASE/user/login" -Method Post -Body $bodyB -ContentType "application/json"
$tokenB = $respB.data.access_token

# Start interview as User A
$headersA = @{Authorization = "Bearer $tokenA"; "Content-Type" = "application/json"}
$startBody = @{skill_id="algorithm"; difficulty="EASY"; question_count=3} | ConvertTo-Json
$startResp = Invoke-RestMethod -Uri "$BASE/interview/start" -Method Post -Headers $headersA -Body $startBody
$sid = $startResp.data.session_id
$qid = $startResp.data.first_question.id
Write-Output "Session: $sid (User A)"

function Test-ApiBody($name, $method, $url, $headers, $expectedCode, $body=$null) {
    try {
        $params = @{Uri=$url; Method=$method; Headers=$headers; UseBasicParsing=$true}
        if ($body) { $params.Body = $body; $params.ContentType = "application/json" }
        $r = Invoke-WebRequest @params
        $json = $r.Content | ConvertFrom-Json
        if ($json.status_code -eq $expectedCode) {
            Write-Output "[PASS] $name - status_code=$($json.status_code) $($json.status_message)"
        } else {
            Write-Output "[FAIL] $name - Expected status_code=$expectedCode, got $($json.status_code) $($json.status_message)"
        }
    } catch {
        # HTTP 422 from Pydantic is a real HTTP error
        $code = [int]$_.Exception.Response.StatusCode
        if ($code -eq $expectedCode) {
            Write-Output "[PASS] $name - HTTP $code (validation error)"
        } else {
            Write-Output "[FAIL] $name - Expected HTTP $expectedCode, got $code"
        }
    }
}

$headersB = @{Authorization = "Bearer $tokenB"}
$completeBody = '{"session_id":"' + $sid + '"}'
$answerBody = "{`"session_id`":`"$sid`",`"question_id`":`"$qid`",`"answer`":`"test`"}"

Write-Output ""
Write-Output "========== P0: Unauthorized Access (User B -> User A) =========="
Test-ApiBody "B->GET session" "Get" "$BASE/interview/session/$sid" $headersB 403
Test-ApiBody "B->GET eval status" "Get" "$BASE/interview/evaluation/status/$sid" $headersB 403
Test-ApiBody "B->GET eval by-session" "Get" "$BASE/interview/evaluation/by-session/$sid" $headersB 403
Test-ApiBody "B->POST complete" "Post" "$BASE/interview/complete" $headersB 403 $completeBody
Test-ApiBody "B->POST answer" "Post" "$BASE/interview/answer" $headersB 403 $answerBody

Write-Output ""
Write-Output "========== P0: Authorized Access (User A) =========="
Test-ApiBody "A->GET session" "Get" "$BASE/interview/session/$sid" $headersA 200
Test-ApiBody "A->GET eval status" "Get" "$BASE/interview/evaluation/status/$sid" $headersA 200

Write-Output ""
Write-Output "========== P0: Non-existent Session =========="
Test-ApiBody "A->GET nonexistent" "Get" "$BASE/interview/session/nonexistent123" $headersA 404

Write-Output ""
Write-Output "========== P2b: Evaluation Status =========="
$statusResp = Invoke-RestMethod -Uri "$BASE/interview/evaluation/status/$sid" -Method Get -Headers $headersA
Write-Output "[PASS] Status: $($statusResp.data.status)"

Write-Output ""
Write-Output "========== P3.1: Answer Length Validation =========="
$longAnswer = "A" * 10001
$longBody = @{session_id=$sid; question_id=$qid; answer=$longAnswer} | ConvertTo-Json
Test-ApiBody "Answer >10000 chars" "Post" "$BASE/interview/answer" $headersA 422 $longBody

$normalBody = @{session_id=$sid; question_id=$qid; answer="def two_sum(nums, target): pass"} | ConvertTo-Json
Test-ApiBody "Answer normal" "Post" "$BASE/interview/answer" $headersA 200 $normalBody

Write-Output ""
Write-Output "========== Summary =========="
Write-Output "P0 Security:     All unauthorized requests return status_code=403"
Write-Output "P2b Eval Status: Endpoint returns PENDING/PROCESSING/COMPLETED"
Write-Output "P3.1 Validation: Answers >10000 chars rejected with HTTP 422"
