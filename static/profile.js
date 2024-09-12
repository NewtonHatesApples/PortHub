function show_textarea() {
    let button = document.getElementById("edit");
    let profile_textarea = document.getElementById("new_profile");
    button.addEventListener("click", function () {
        if (profile_textarea.hidden) {
            button.textContent = "Cancel";
            profile_textarea.hidden = false;
            change_button_disable();
        } else {
            button.textContent = "Edit profile ...";
            profile_textarea.hidden = true;
            change_button_enable();
        }
    })
}

function validate_blank() {
    let profile_textarea = document.getElementById("new_profile");
    profile_textarea.addEventListener("input", function() {
        if (profile_textarea.value === "") {
            change_submit_button_disable();
        } else {
            change_submit_button_enable();
        }
    })
}

function change_button_enable() {
    let button = document.getElementById("edit");
    button.style.background = "#FF9900";
    button.style.color = "black";
}

function change_button_disable() {
    let button = document.getElementById("edit");
    button.style.background = "#2a2626";
    button.style.color = "white";
}

function change_submit_button_disable() {
    let button = document.getElementById("submit_button");
    button.style.background = "#2a2626";
    button.style.color = "white";
    button.style.cursor = "default";
    button.disabled = true;
}

function change_submit_button_enable() {
    let button = document.getElementById("submit_button");
    button.style.background = "#ff9900";
    button.style.color = "black";
    button.style.cursor = "pointer";
    button.hidden = false;
    button.disabled = false;
}

document.addEventListener("DOMContentLoaded", function() {
    show_textarea();
    document.getElementById("submit_button").hidden = true;
    change_submit_button_disable();
    validate_blank();
})
