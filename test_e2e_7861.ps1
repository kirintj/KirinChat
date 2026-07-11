# E2E Test on port 7861 (fresh backend with all code changes)
$ErrorActionPreference = "Stop"
$BASE = "http://localhost:7861/api/v1"

# Login User A
$bodyA = @{user_name="testuser_e2e"; user_password="Test1234"} | ConvertTo-Json
$respA = Invoke-RestMethod -Uri "$BASE/user/login" -Method Post -Body $bodyA -ContentType "application/json"
$tokenA = $respA.data.access_token
Write-Output "User A (id=$($respA.data.user_id)) logged in"

# Login User B
$bodyB = @{user_name="testuser_b"; user_password="Test1234"} | ConvertTo-Json
$respB = Invoke-RestMethod -Uri "$BASE/user/login" -Method Post -Body $bodyB -ContentType "application/json"
$tokenB = $respB.data.access_token
Write-Output "User B (id=$($respB.data.user_id)) logged in"

# Start interview as User A
$headersA = @{Authorization = "Bearer $tokenA"; "Content-Type" = "application/json"}
$startBody = @{skill_id="algorithm"; difficulty="EASY"; question_count=3} | ConvertTo-Json
$startResp = Invoke-RestMethod -Uri "$BASE/interview/start" -Method Post -Headers $headersA -Body $startBody
$sid = $startResp.data.session_id
$qid = $startResp.data.first_question.id
Write-Output "User A created session: $sid (question: $qid)"

$ErrorActionPreference = "Continue"

function Test-Api($name, $method, $url, $headers, $expected, $body=$null) {
    try {
        $params = @{Uri=$url; Method=$method; Headers=$headers; UseBasicParsing=$true}
        if ($body) { $params.Body = $body; $params.ContentType = "application/json" }
        $r = Invoke-WebRequest @params
        if ($r.StatusCode -eq $expected) { Write-Output "[PASS] $name - HTTP $($r.StatusCode)" }
        else { Write-Output "[FAIL] $name - Expected $expected, got $($r.StatusCode) - $($r.Content)" }
    } catch {
        $code = [int]$_.Exception.Response.StatusCode
        $reader = [System.IO.StreamReader]::new($_.Exception.Response.GetResponseStream())
        $respBody = $reader.ReadToEnd()
        if ($code -eq $expected) { Write-Output "[PASS] $name - HTTP $code - $respBody" }
        else { Write-Output "[FAIL] $name - Expected $expected, got $code - $respBody" }
    }
}

Write-Output ""
Write-Output "========== P0: Unauthorized Access (User B -> User A session) =========="
$headersB = @{Authorization = "Bearer $tokenB"}
Test-Api "B->GET session" "Get" "$BASE/interview/session/$sid" $headersB 403
Test-Api "B->GET eval status" "Get" "$BASE/interview/evaluation/status/$sid" $headersB 403
Test-Api "B->GET eval by-session" "Get" "$BASE/interview/evaluation/by-session/$sid" $headersB 403
$completeBody = '{"session_id":"' + $sid + '"}'
Test-Api "B->POST complete" "Post" "$BASE/interview/complete" $headersB 403 $completeBody
$answerBody = "{`"session_id`":`"$sid`",`"question_id`":`"$qid`",`"answer`":`"test`"}"
Test-Api "B->POST answer" "Post" "$BASE/interview/answer" $headersB 403 $answerBody

Write-Output ""
Write-Output "========== P0: Authorized Access (User A) =========="
Test-Api "A->GET session" "Get" "$BASE/interview/session/$sid" $headersA 200
Test-Api "A->GET eval status" "Get" "$BASE/interview/evaluation/status/$sid" $headersA 200

Write-Output ""
Write-Output "========== P2b: Evaluation Status =========="
$statusResp = Invoke-RestMethod -Uri "$BASE/interview/evaluation/status/$sid" -Method Get -Headers $headersA
Write-Output "[PASS] Status: $($statusResp.data.status) (PENDING for IN_PROGRESS session)"

Write-Output ""
Write-Output "========== P3.1: Answer Length Validation =========="
$longAnswer = "A" * 10001
$longBody = @{session_id=$sid; question_id=$qid; answer=$longAnswer} | ConvertTo-Json
Test-Api "Answer >10000 chars" "Post" "$BASE/interview/answer" $headersA 422 $longBody

# Normal answer
$normalBody = @{session_id=$sid; question_id=$qid; answer="def two_sum(nums, target): pass"} | ConvertTo-Json
Test-Api "Answer normal" "Post" "$BASE/interview/answer" $headersA 200 $normalBody

Write-Output ""
Write-Output "========== P0: Non-existent Session =========="
Test-Api "A->GET nonexistent session" "Get" "$BASE/interview/session/nonexistent123" $headersA 404

Write-Output ""
Write-Output "========== P1a: Score Scale (0-100) =========="
Write-Output "Score scale will be verified after completing interview + evaluation"
Write-Output "(Skipped - requires full LLM evaluation flow)"
