document.addEventListener('DOMContentLoaded', function () {

    function load_search () {
        let search_value = document.getElementById("search_bar").value;
        let search_iframe = document.getElementById("search");
        search_iframe.src = "/search?q=" + search_value;
        search_iframe.hidden = search_value === "";
    }

    window.load_search = load_search;
});
