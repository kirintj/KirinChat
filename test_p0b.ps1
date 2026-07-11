$tokenB = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ7XCJ1c2VyX25hbWVcIjogXCJ0ZXN0dXNlcl9iXCIsIFwidXNlcl9pZFwiOiBcIjRcIiwgXCJyb2xlXCI6IFtdfSIsImlhdCI6MTc4MzcwNDc4NSwibmJmIjoxNzgzNzA0Nzg1LCJqdGkiOiI4MzkzZmI5Ny05ZjhmLTQ2MWEtYjM1Ny0zMDFhZWM4YmM0OTMiLCJleHAiOjE3ODM3OTExODUsInR5cCI6ImFjY2VzcyIsImZyZXNoIjpmYWxzZX0.nyYZ-HmLxO8npelFvUThHl6CePCQegq77LXSTjRn9f8"
$headersB = @{Authorization = "Bearer $tokenB"}

Write-Output "=== User B on /interview/history (should work) ==="
try {
    $r = Invoke-WebRequest -Uri "http://localhost:7860/api/v1/interview/history" -Method Get -Headers $headersB -UseBasicParsing
    Write-Output "HTTP $($r.StatusCode) - PASS"
} catch {
    $code = [int]$_.Exception.Response.StatusCode
    $reader = [System.IO.StreamReader]::new($_.Exception.Response.GetResponseStream())
    $body = $reader.ReadToEnd()
    Write-Output "HTTP $code - $body"
}

Write-Output ""
Write-Output "=== User B on /skill/list (should work) ==="
try {
    $r = Invoke-WebRequest -Uri "http://localhost:7860/api/v1/skill/list" -Method Get -Headers $headersB -UseBasicParsing
    Write-Output "HTTP $($r.StatusCode) - PASS"
} catch {
    $code = [int]$_.Exception.Response.StatusCode
    $reader = [System.IO.StreamReader]::new($_.Exception.Response.GetResponseStream())
    $body = $reader.ReadToEnd()
    Write-Output "HTTP $code - $body"
}

Write-Output ""
Write-Output "=== User B on /interview/session/nonexistent (should 404 or 403) ==="
try {
    $r = Invoke-WebRequest -Uri "http://localhost:7860/api/v1/interview/session/nonexistent-id" -Method Get -Headers $headersB -UseBasicParsing
    Write-Output "HTTP $($r.StatusCode) - $($r.Content)"
} catch {
    $code = [int]$_.Exception.Response.StatusCode
    $reader = [System.IO.StreamReader]::new($_.Exception.Response.GetResponseStream())
    $body = $reader.ReadToEnd()
    Write-Output "HTTP $code - $body"
}
