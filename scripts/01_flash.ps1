$KVASER_PATH = "C:\Program Files (x86)\Kvaser\Canlib\Bin"
$BUILD_DIR = "build\kvaser"
$FILE = "preproc.txe"

if ( -not ( Test-Path $KVASER_PATH ) ) {
    Write-Host "Kvaser's CANlib SDK is not installed."
    Write-Host "https://www.kvaser.com/developer/canlib-sdk/"
    Write-Host "In case it is installed in non default location, modify this file."
}
elseif ( -not ( Test-Path "..\$BUILD_DIR\$FILE" ) ) {
  Write-Host "Couldn't locate '$FILE' inside '$BUILD_DIR'"
}
else {
  # Iterate over all t files in SOURCE_DIR
  try {
    Write-Host "Flashing $FILE ..."
    $options = @{
      FilePath = "$KVASER_PATH\tutil.exe"
      WorkingDirectory = "..\$BUILD_DIR"
      ArgumentList = "-channel=0 -slot=0 -load $FILE -start"
    } 
    # Build file
    $scc = Start-Process @options -NoNewWindow -PassThru
    $scc.WaitForExit()
  }
  catch {
    Write-Host "Flashing failed prematurely."
  }
  Write-Host -NoNewLine "Press any key to continue..."
  $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}
# SIG # Begin signature block
# MIIFlAYJKoZIhvcNAQcCoIIFhTCCBYECAQExCzAJBgUrDgMCGgUAMGkGCisGAQQB
# gjcCAQSgWzBZMDQGCisGAQQBgjcCAR4wJgIDAQAABBAfzDtgWUsITrck0sYpfvNR
# AgEAAgEAAgEAAgEAAgEAMCEwCQYFKw4DAhoFAAQUF9pOk5fD+gJRFz36S5eAk1bQ
# kE+gggMiMIIDHjCCAgagAwIBAgIQGfr7ZythKp9IPSDyM3gd3zANBgkqhkiG9w0B
# AQsFADAnMSUwIwYDVQQDDBxQb3dlclNoZWxsIENvZGUgU2lnbmluZyBDZXJ0MB4X
# DTIzMDMyODE1MjU1M1oXDTI0MDMyODE1NDU1M1owJzElMCMGA1UEAwwcUG93ZXJT
# aGVsbCBDb2RlIFNpZ25pbmcgQ2VydDCCASIwDQYJKoZIhvcNAQEBBQADggEPADCC
# AQoCggEBANC0lS39vz5/pFcEmUd0jfPtg/9BsZtyusriHEhEE5/hnrNyL51LTdfp
# dek9WmhHqZ5OYAEQVk3WZ6OJ+TDqwh3VZd4HhTUcQGZXJLQbdPHUsx3Q2qgXi88B
# W6zZO/5pqTR/awaz/y3GoikU4mA0+pblThmtsKNVv7ILFNJ9SZJjzfIO2q83k7pd
# rm7IDvNAkRHQfL7eHa7274A4KkoijnTOp163eLhW5gLwOTr5XI/qgl2BL3NXoBe+
# 5insxvARlT9JBQqKJLCv0GOzVvlT/7Q52pssZfKHnNz9Ia0xFgEPWmpqAcNoUZwT
# 1JFDZqHX4/FcmpddMJC4Jmb4lrFmoBECAwEAAaNGMEQwDgYDVR0PAQH/BAQDAgeA
# MBMGA1UdJQQMMAoGCCsGAQUFBwMDMB0GA1UdDgQWBBRliJaMrDOp0VAmx9iyRYAp
# kCgz6TANBgkqhkiG9w0BAQsFAAOCAQEAP7z++FbmF+JciZnkg9q7q+gy6m7lfiSQ
# BbCV46O1jgynxR5kPWOERh28WMlf7g/oSBqdUVVmmosNBhLCnX4hAwBu+1gsutH2
# jMXtbpZQ5iZ5Q7jD1gQl16sDJHMa/bj/UjaZeKYRrkx6NX7sr1/1x1HJ6SJH93qN
# DIgCnQR9MZ+hEH32dKlED7SxwjgNHd5R1tNJ/h/P3Lz4BrsE8tt/7+4+Mq62S//y
# ek9sjwava1L57Zhn9vweZ3hNI70plibCHQ1hoWwCflAxwnrib2zMGVG1K3tkuiQn
# HRYslSRYfSraWwtq4XBAuNRo5WOdcMrQo66q14cOMFo0Fo76zjKSSDGCAdwwggHY
# AgEBMDswJzElMCMGA1UEAwwcUG93ZXJTaGVsbCBDb2RlIFNpZ25pbmcgQ2VydAIQ
# Gfr7ZythKp9IPSDyM3gd3zAJBgUrDgMCGgUAoHgwGAYKKwYBBAGCNwIBDDEKMAig
# AoAAoQKAADAZBgkqhkiG9w0BCQMxDAYKKwYBBAGCNwIBBDAcBgorBgEEAYI3AgEL
# MQ4wDAYKKwYBBAGCNwIBFTAjBgkqhkiG9w0BCQQxFgQU8lAUlW4tOWwLY0tkjn0Y
# F775pJUwDQYJKoZIhvcNAQEBBQAEggEAn6w3jR8gxTPIOjlKg4yVXO4L3tEn7UDJ
# TLf3orVCOvaCWaAaha5o4vB3n6rnfCWGxnPCKX9I2K1kLXmkEnu6uFxrDVYg0PVv
# FpXUkHpGYyqfeaz7RCepbdSb6ENSS7p2p+pf6HsTshbRWWdmGq71wbNIKDTxSEK8
# 5ttZoEl7jc1qmMMcsVvvtwhdzsZtp4LfrwKCuQ1UATAJNd6kBc24BMyOCagPf81j
# AfT8k4w+4kTUe23VmeloC8MBVRojJK3n2aZ5MmeH1/F4RhQNPNJYNMcKZOc4RR+a
# paI0K9HYthyRROjZNPhJpq9u1O3Sg4dX9N+YIgrltSapFohr40QXKA==
# SIG # End signature block
