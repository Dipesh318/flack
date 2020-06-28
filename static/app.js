document.addEventListener('DOMContentLoaded',()=>{
    console.log("DOM")
    var socket = io.connect('http://' + document.domain + ':' + location.port);
    var localStorage = window.localStorage;
    
    socket.on('connect', () => {
        
        socket.emit("joined")


        document.querySelector('#msg').addEventListener("keydown", event => {
            if (event.key == "Enter") {
                document.getElementById("send").click();
            }
        })

        document.querySelector("#send").addEventListener('click',()=>{
            var message = document.querySelector("#msg").value
            document.querySelector("#msg").value = ""
            var today = new Date();
            var date = today.getFullYear()+'-'+(today.getMonth()+1)+'-'+today.getDate();
            var time = today.getHours() + ":" + today.getMinutes() + ":" + today.getSeconds();
            var timestamp = date+' '+time;
            socket.emit("send message", {'message' : message, 'time' : timestamp})

        })

        

        document.querySelector('#leave').addEventListener('click', () => {
            socket.emit('left');
            $(".chat").append("<p class='text-muted'>"+data.msg+"</p>")
            localStorage.removeItem('channel');
            window.location.replace('/');
        })

        document.querySelector('#logout').addEventListener('click', () => {
            localStorage.removeItem('channel');
        })


    });
    socket.on('status join', data => {
        $(".chat").append("<p class='text-muted'>"+data.msg+"</p>")
        
          
        localStorage.setItem('channel', data.channel)
        
       
        
        
    })

    socket.on('status left', data => {
        $(".user-logs").textContent=''
        localStorage.removeItem('channel', data.channel)
    })

    socket.on("show msg", data=>{
        console.log(data)
        $(".chat").append("<p class='chat-message'><span class='text-muted'><i><strong>"+data.user+"</strong></i><br>"+data.time+"</span><br>"+data.message+"</p>")
    });
});

