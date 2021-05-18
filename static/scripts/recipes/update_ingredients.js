function set_listeners () {
    // get ahold of and count all buttons
    let buttons = document.getElementsByTagName('button');
    let length = buttons.length

    for (i=0; i<length; i++) {
        // determine type of buttons
        let button_id = buttons.item(i).id;
        let button_type = button_id.slice(0, 3);
        // get the id of the ingquant to deal with
        let button_ingquant = button_id.slice(4);
        
        // if buttons are edit or remove, add an event listener
        if (button_type == 'edt' || button_type == "rem") {
            buttons.item(i).addEventListener("click", function () {
                update_ingredients(button_type, button_ingquant)
            });    
        }
    }
}

function update_ingredients (button_type, button_ingquant) {
    const endpoint = "/recipes/update_ingredients/";
    const user_id = JSON.parse(document.getElementById('user_id').textContent);
    $.ajax({
        type: "POST",
        url: endpoint,
        data:{
            'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val(),
            tag: button_type,
            user_id: user_id,
            ingquant_id: button_ingquant
        },
        datatype:'json',
        success: function(data) {
            if (data['success']) {
                let ing_div = $('#ingredients_list');
            
                // fade out the ing_div, then:
                ing_div.fadeTo('fast', 0).promise().then(() => {
                    // replace the HTML contents
                    ing_div.html(data['html_from_view'])
                    // fade-in the div with new contents
                    ing_div.fadeTo('fast', 1)
                    set_listeners();
                });                
            }
        }
    });
}


$(function(){ // this will be called when the DOM is ready
    set_listeners();
});