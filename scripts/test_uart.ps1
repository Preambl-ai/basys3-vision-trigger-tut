param(
    [Parameter(Mandatory)]
    [string] $Port
)

$ErrorActionPreference = 'Stop'
$serial = [IO.Ports.SerialPort]::new($Port, 115200, 'None', 8, 'One')
try {
    $serial.ReadTimeout = 2000
    $serial.WriteTimeout = 2000
    $serial.Open()
    $serial.DiscardInBuffer()

    [byte[]] $message = @(0x41)
    $serial.Write($message, 0, $message.Length)
    try {
        $reply = $serial.ReadByte()
    } catch [TimeoutException] {
        throw "Sent A on $Port but received no reply. Check that uart_echo.bit is loaded."
    }

    if ($reply -ne $message[0]) {
        throw ('Sent A (0x41) but received 0x{0:X2} on {1}.' -f $reply, $Port)
    }

    Write-Output "PASS: sent A and received A on $Port."
} finally {
    $serial.Dispose()
}
