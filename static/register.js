function change_button_enable() {
    let button = document.getElementById("submit_button");
    button.style.background = "#FF9900";
    button.style.color = "black";
    button.disabled = false;
    button.style.cursor = "pointer";
}

function change_button_disable() {
    let button = document.getElementById("submit_button");
    button.style.background = "#2a2626";
    button.style.color = "white";
    button.disabled = true;
    button.style.cursor = "default";
}

function get_sum() {
    let user_len = document.getElementById("username").value.length;
    let pass_len = document.getElementById("password").value.length;
    if (user_len >= 4 && user_len <= 16 && pass_len >= 8) {
        change_button_enable();
    }
    else {
        change_button_disable();
    }
}