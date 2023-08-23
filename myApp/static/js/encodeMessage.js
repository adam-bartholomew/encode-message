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

function validateLogin() {
    let invalidName = false;
    let invalidPwd = false;
    if(document.getElementById('loginUsername').value.length < 1){
        document.getElementById('loginUsername').style.borderColor = "red";
        invalidName = true;
    } else {
        document.getElementById('loginUsername').style.borderColor = "";
    }

    if(document.getElementById('loginPassword').value.length < 1){
        document.getElementById('loginPassword').style.borderColor = "red";
        invalidPwd = true;
    } else {
        document.getElementById('loginUsername').style.borderColor = "";
    }

    if(!invalidName && !invalidPwd){
        document.getElementById('loading').style.display = "block";
    }
}

function validateRegister() {
    let invalidName = false;
    let invalidPwd = false;
    if(document.getElementById('registerUsername').value.length < 1){
        document.getElementById('registerUsername').style.borderColor = "red";
        invalidName = true;
    } else {
        document.getElementById('registerUsername').style.borderColor = "";
    }

    if(document.getElementById('registerPassword').value.length < 8 || document.getElementById('registerPassword').value.length > 25){
        document.getElementById('registerPassword').style.borderColor = "red";
        invalidPwd = true;
    } else {
        document.getElementById('registerPassword').style.borderColor = "";
    }

    if(!invalidName && !invalidPwd){
        document.getElementById('loading').style.display = "block";
    }
}

/* Functions to display the spinning loader wheel */
function loadingGeneral() {
    document.getElementById('loading').style.display = "block";
}

function loadingMessage() {
    if(document.URL.endsWith("/encode")){
        if(document.getElementById('encodeInputMessage').value != ""){
            document.getElementById('loading').style.display = "block";
        }
    }

    if(document.URL.endsWith("/decode")){
        if(document.getElementById('decodeInputMessage').value != ""){
            document.getElementById('loading').style.display = "block";
        }
    }
}