function change_button_enable() {
    let button = document.getElementById("submit_button");
    button.style.background = "#FF9900";
    button.disabled = false;
    button.style.color = "black";
    button.style.cursor = "pointer";
}

function change_button_disable() {
    let button = document.getElementById("submit_button");
    button.style.background = "#2a2626";
    button.style.color = "white";
    button.disabled = true;
    button.style.cursor = "default";
}

function previewFile() {
    const fileInput = document.getElementById('upload_file');
    const previewImage = document.getElementById('preview_image');
    const file = fileInput.files[0];
    const reader = new FileReader();

    reader.onloadend = function () {
        previewImage.src = reader.result;
    }

    if (file) {
        reader.readAsDataURL(file);
        previewImage.hidden = false;
        change_button_enable()
    } else {
        previewImage.hidden = true;
        change_button_disable()
    }
}