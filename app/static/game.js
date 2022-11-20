var socket = io();

socket.addEventListener("message", (data) => {
    console.log("received message: " + data);
    var div = document.createElement('div');
    div.setAttribute("class", "alert alert-dismissible alert-secondary");
    div.setAttribute("style", "position: fixed; left: 10px; right: 10px; bottom: 0px;");
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
