$tokenA = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ7XCJ1c2VyX25hbWVcIjogXCJ0ZXN0dXNlcl9lMmVcIiwgXCJ1c2VyX2lkXCI6IFwiM1wiLCBcInJvbGVcIjogW119IiwiaWF0IjoxNzgzNzA0NjU0LCJuYmYiOjE3ODM3MDQ2NTQsImp0aSI6Ijk0MmYyZDViLWM5YWEtNDZhZi1hZDQyLWQ1NjFlNjFlZDkxMSIsImV4cCI6MTc4Mzc5MTA1NCwidHlwZSI6ImFjY2VzcyIsImZyZXNoIjpmYWxzZX0.QaSU-_T-CS-0n7LV3HdAzSaKWco9yPJ5tvj3k3IRMTA"
$tokenB = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ7XCJ1c2VyX25hbWVcIjogXCJ0ZXN0dXNlcl9iXCIsIFwidXNlcl9pZFwiOiBcIjRcIiwgXCJyb2xlXCI6IFtdfSIsImlhdCI6MTc4MzcwNDc4NSwibmJmIjoxNzgzNzA0Nzg1LCJqdGkiOiI4MzkzZmI5Ny05ZjhmLTQ2MWEtYjM1Ny0zMDFhZWM4YmM0OTMiLCJleHAiOjE3ODM3OTExODUsInR5cCI6ImFjY2VzcyIsImZyZXNoIjpmYWxzZX0.nyYZ-HmLxO8npelFvUThHl6CePCQegq77LXSTjRn9f8"
$sid = "4c467f84ef004253bf92ac5874e696a5"
$headersB = @{Authorization = "Bearer $tokenB"}
$headersA = @{Authorization = "Bearer $tokenA"}

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
