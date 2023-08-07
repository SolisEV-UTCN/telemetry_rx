$KVASER_PATH = "C:\Program Files (x86)\Kvaser\Canlib\Bin"
$SOURCE_DIR = "src\plug&play\kvaser"
$BUILD_DIR = "build\kvaser"

if ( Test-Path $KVASER_PATH ) {
  try {
    # Iterate over all t files in SOURCE_DIR
    $files = Get-ChildItem -Path "..\$SOURCE_DIR" -Name -Include *.t
    foreach ($file in $files) {
      Write-Host "Compiling $file ..."
      $options = @{
        FilePath = "$KVASER_PATH\scc.exe"
        WorkingDirectory = ".."
        ArgumentList = "-o$BUILD_DIR $SOURCE_DIR\$file"
      } 
      # Build file
      $scc = Start-Process @options -NoNewWindow -PassThru
      $scc.WaitForExit()
    }
  }
  catch {
    Write-Host "Build failed prematurely."
  }
  Write-Host -NoNewLine "Press any key to continue..."
  $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}
else {
  Write-Host "Kvaser's CANlib SDK is not installed."
  Write-Host "https://www.kvaser.com/developer/canlib-sdk/"
  Write-Host "In case it is installed in non default location, modify this file."
}
# SIG # Begin signature block
# MIIFlAYJKoZIhvcNAQcCoIIFhTCCBYECAQExCzAJBgUrDgMCGgUAMGkGCisGAQQB
# gjcCAQSgWzBZMDQGCisGAQQBgjcCAR4wJgIDAQAABBAfzDtgWUsITrck0sYpfvNR
# AgEAAgEAAgEAAgEAAgEAMCEwCQYFKw4DAhoFAAQU0EbS/Cy0FcaV3O7lKt+LfhpM
# Q2WgggMiMIIDHjCCAgagAwIBAgIQGfr7ZythKp9IPSDyM3gd3zANBgkqhkiG9w0B
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
# MQ4wDAYKKwYBBAGCNwIBFTAjBgkqhkiG9w0BCQQxFgQUTAYadtTV9KOpM/0eKfSO
# slZkmA4wDQYJKoZIhvcNAQEBBQAEggEAKvpQwKhxIZyxBcWZT6TzUCzr2vk2/Nrm
# YIq1uG3m0ZtsLT89PpTJBI9fXJkNPmw3YzjYuw4590E33KCaVsWDL8nGYvtCF0jf
# cDjq7C/xo52lIFMAHjo/e18l1IDbRZNGfY4ROgafuWFuARcmP6yEscS72a5TJGN+
# CYOKB/zcpZ5EmUIZQ4IXMJ0c8ReRTgcDFvUSgn7FoXlHWe19YCdjwuMk5SU+gL67
# YcS7wDT8O7OsxTigqPb4g1dAWuh39F6YS36qKJQQEXSeSC6A01MFqNYOh89BOKtZ
# C6PB+ctzofK9t4ne/+vjBgFia55I/ugpHfApV51qEW/jJqAa6SjKBQ==
# SIG # End signature block
