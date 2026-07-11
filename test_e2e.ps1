# E2E Test: Login fresh, test P0 security
$ErrorActionPreference = "Stop"

# Login User A
$bodyA = @{user_name="testuser_e2e"; user_password="Test1234"} | ConvertTo-Json
$respA = Invoke-RestMethod -Uri "http://localhost:7860/api/v1/user/login" -Method Post -Body $bodyA -ContentType "application/json"
$tokenA = $respA.data.access_token
Write-Output "User A (id=$($respA.data.user_id)) logged in"

# Login User B
$bodyB = @{user_name="testuser_b"; user_password="Test1234"} | ConvertTo-Json
$respB = Invoke-RestMethod -Uri "http://localhost:7860/api/v1/user/login" -Method Post -Body $bodyB -ContentType "application/json"
$tokenB = $respB.data.access_token
Write-Output "User B (id=$($respB.data.user_id)) logged in"

# Start interview as User A
$headersA = @{Authorization = "Bearer $tokenA"; "Content-Type" = "application/json"}
$startBody = @{skill_id="algorithm"; difficulty="EASY"; question_count=3} | ConvertTo-Json
$startResp = Invoke-RestMethod -Uri "http://localhost:7860/api/v1/interview/start" -Method Post -Headers $headersA -Body $startBody
$sid = $startResp.data.session_id
Write-Output "User A created session: $sid"

# Test P0: User B tries to access User A's session
$headersB = @{Authorization = "Bearer $tokenB"}
$ErrorActionPreference = "Continue"

function Test-Api($name, $method, $url, $headers, $expected, $body=$null) {
    try {
        $params = @{Uri=$url; Method=$method; Headers=$headers; UseBasicParsing=$true}
        if ($body) { $params.Body = $body; $params.ContentType = "application/json" }
        $r = Invoke-WebRequest @params
        if ($r.StatusCode -eq $expected) { Write-Output "[PASS] $name - HTTP $($r.StatusCode)" }
        else { Write-Output "[FAIL] $name - Expected $expected, got $($r.StatusCode)" }
    } catch {
        $code = [int]$_.Exception.Response.StatusCode
        $reader = [System.IO.StreamReader]::new($_.Exception.Response.GetResponseStream())
        $respBody = $reader.ReadToEnd()
        if ($code -eq $expected) { Write-Output "[PASS] $name - HTTP $code - $respBody" }
        else { Write-Output "[FAIL] $name - Expected $expected, got $code - $respBody" }
    }
}

Write-Output ""
Write-Output "========== P0: Unauthorized Access (User B -> User A) =========="
Test-Api "B->GET session" "Get" "http://localhost:7860/api/v1/interview/session/$sid" $headersB 403
Test-Api "B->GET eval status" "Get" "http://localhost:7860/api/v1/interview/evaluation/status/$sid" $headersB 403
Test-Api "B->GET eval by-session" "Get" "http://localhost:7860/api/v1/interview/evaluation/by-session/$sid" $headersB 403
$completeBody = '{"session_id":"' + $sid + '"}'
Test-Api "B->POST complete" "Post" "http://localhost:7860/api/v1/interview/complete" $headersB 403 $completeBody

Write-Output ""
Write-Output "========== P0: Authorized Access (User A) =========="
Test-Api "A->GET session" "Get" "http://localhost:7860/api/v1/interview/session/$sid" $headersA 200
Test-Api "A->GET eval status" "Get" "http://localhost:7860/api/v1/interview/evaluation/status/$sid" $headersA 200

Write-Output ""
Write-Output "========== P2b: Evaluation Status =========="
$statusResp = Invoke-RestMethod -Uri "http://localhost:7860/api/v1/interview/evaluation/status/$sid" -Method Get -Headers $headersA
Write-Output "Status: $($statusResp.data.status) (expected PENDING for IN_PROGRESS session)"

Write-Output ""
Write-Output "========== P3.1: Answer Length Validation =========="
# Get first question ID
$qid = $startResp.data.first_question.id
$longAnswer = "A" * 10001
$answerBody = @{session_id=$sid; question_id=$qid; answer=$longAnswer} | ConvertTo-Json
Test-Api "Answer >10000 chars" "Post" "http://localhost:7860/api/v1/interview/answer" $headersA 422 $answerBody

# Normal answer should work
$normalAnswer = "This is a test answer"
$answerBody2 = @{session_id=$sid; question_id=$qid; answer=$normalAnswer} | ConvertTo-Json
Test-Api "Answer normal length" "Post" "http://localhost:7860/api/v1/interview/answer" $headersA 200 $answerBody2
