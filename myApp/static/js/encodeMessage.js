function clearEncodeForm() {
    document.getElementById('encodeInputMessage').value = "";
    document.getElementById('encodeOffset').value = "";
    document.getElementById('encodedMessage').value = "";
}

function clearDecodeForm() {
    document.getElementById('decodeInputMessage').value = "";
    document.getElementById('decodeOffset').value = "";
    document.getElementById('decodedMessage').value = "";
}

function copyToClipboard(elementId) {
    let text = document.getElementById(elementId)
    text.select()
    navigator.clipboard.writeText(text.value)
}

/* Displays the spinning loader wheel */
function loading(){
    if(document.getElementById('encodeInputMessage').value != "" || document.getElementById('decodeInputMessage').value != ""){
        document.getElementById('loading').style.display = "block";
    }
}