function handleImageBotResponse(response) {
    var botHtml = '<div class="botText"><span>' + response + '</span></div>';
    $("#image-chat-box").append(botHtml); // Display model response in the image-chat-box
    $("#image-chat-box").scrollTop($("#image-chat-box")[0].scrollHeight); // Scrolls to the bottom of the image-chat-box
}

function handleTextBotResponse(response) {
    var botHtml = '<div class="botText"><span>' + response + '</span></div>';
    $("#text-chat-box").append(botHtml); // Display model response in the text-chat-box
    $("#text-chat-box").scrollTop($("#text-chat-box")[0].scrollHeight); // Scrolls to the bottom of the text-chat-box
}

function handleUserInput(rawText) {
    var userHtml = '<div class="userText"><span>' + rawText + '</span></div>';
    $("#text-chat-box").append(userHtml); // Append user input to the text-chat-box
    $("#text-chat-box").scrollTop($("#text-chat-box")[0].scrollHeight); // Scrolls to the bottom of the text-chat-box
}

$(document).ready(function() {
    $("#uploadForm").submit(function(e) {
        e.preventDefault();
        var formData = new FormData(this);

        $.ajax({
            url: '/predict',
            type: 'POST',
            data: formData,
            contentType: false,
            processData: false,
            success: function(response) {
                var prediction = response.prediction;
                handleImageBotResponse(prediction); // Display image prediction in image-chat-box
            },
            error: function(error) {
                console.log(error);
            }
        });
    });

    $("#sendButton").click(function() {
        var rawText = $("#text-input").val();
        if (rawText.trim() === "") {
            return;
        }
        handleUserInput(rawText); // Display user input in text-chat-box

        $.get("/get", { msg: rawText }).done(function(data) {
            handleTextBotResponse(data); // Display model response in text-chat-box
        });

        $("#text-input").val(""); // Clear input field after sending
    });

    $("#text-input").keypress(function(e) {
        if (e.which == 13) { // Enter key press triggers the handleUserInput function
            var rawText = $("#text-input").val();
            if (rawText.trim() === "") {
                return;
            }
            handleUserInput(rawText); // Display user input in text-chat-box

            $.get("/get", { msg: rawText }).done(function(data) {
                handleTextBotResponse(data); // Display model response in text-chat-box
            });

            $("#text-input").val(""); // Clear input field after sending
        }
    });
});

function previewImage() {
    const fileInput = document.getElementById('image-input');
    const chatBox = document.getElementById('image-chat-box');
    
    if (fileInput.files && fileInput.files[0]) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            const image = document.createElement('img');
            image.src = e.target.result;
            image.style.maxWidth = '100%';
            image.style.maxHeight = '300px';
            chatBox.innerHTML = '';
            chatBox.appendChild(image);
        }
        
        reader.readAsDataURL(fileInput.files[0]);
    }
}
