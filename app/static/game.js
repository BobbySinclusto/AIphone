var socket = io();

function show_message(message) {
    var div = document.createElement('div');
    div.setAttribute("class", "alert alert-dismissible alert-secondary");
    div.setAttribute("style", "position: fixed; left: 10px; right: 10px; top: 0px;");
    var button = document.createElement('button');
    button.setAttribute("type", "button");
    button.setAttribute("class", "btn-close");
    button.setAttribute("data-bs-dismiss", "alert");
    div.appendChild(button);
    div.appendChild(document.createTextNode(message));
    document.body.appendChild(div);

    setTimeout(()=>{div.remove()}, 5000);
}

socket.addEventListener("message", (data) => {
    console.log("received message: " + data);
    show_message(data);
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

let random_prompt_button  = document.getElementById("random_prompt_button");
if (random_prompt_button) {
    random_prompt_button.addEventListener('click', function() {
        this.disabled = true;
        fetch(
            '/random_prompt',
            {method: 'POST'}
        ).then(response => {
            if (response.status != 200) {
                throw new Error('Could not generate a random prompt, please try again. If the issue persists, just make up your own prompt.')
            }
            return response.json();
        }).then(data => {
            document.getElementById("prompt").value = data.prompt;
        }).catch(error => {
            show_message(error.message);
        }).finally(() => {
            this.disabled = false;
        });
    });
}
