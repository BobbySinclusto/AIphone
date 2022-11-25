var socket = io();

socket.addEventListener("message", (data) => {
    console.log("received message: " + data);
    var div = document.createElement('div');
    div.setAttribute("class", "alert alert-dismissible alert-secondary");
    div.setAttribute("style", "position: fixed; left: 10px; right: 10px; top: 0px;");
    var button = document.createElement('button');
    button.setAttribute("type", "button");
    button.setAttribute("class", "btn-close");
    button.setAttribute("data-bs-dismiss", "alert");
    div.appendChild(button);
    div.appendChild(document.createTextNode(data));
    document.body.appendChild(div);

    setTimeout(()=>{div.remove()}, 5000);
});

socket.addEventListener("reload", (data) => {
    location.reload();
});

socket.addEventListener("game_info", (data) => {
    info_do_dad = document.getElementById("info_do_dad");
    Array.from(info_do_dad.children).forEach((row, i) => {
        row.children[0].textContent = data[i]["name"];
        row.children[1].textContent = data[i]["status"];
    });
});
