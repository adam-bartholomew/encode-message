function clearEncodeForm() {
    document.getElementById('inputMessage').value = "";
    document.getElementById('encodeOffset').value = "";
    document.getElementById('encodedMessage').value = "";
}

function clearDecodeForm() {
    document.getElementById('inputMessage').value = "";
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
    if(document.getElementById('inputMessage').value != ""){
        document.getElementById("loading").style.display = "block";
    }
}