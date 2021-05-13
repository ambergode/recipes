// This function based on https://morioh.com/p/560b11927857

function record_button (evt, button_type, button_recipe) {
    evt.preventDefault(); 
    const recipe_id = button_recipe;
    const endpoint = "/recipes/button_ajax/";
    const user_id = JSON.parse(document.getElementById('user_id').textContent);

    let symbols_dict = {
        favorite: {
            "button_id": "sub_fav",
            "add": '<i class="fas fa-heart" style="color:#ab0000"></i>',
            "remove": '<i class="far fa-heart" style="color:grey"></i>'
        },
        shop:{
            "button_id": "sub_shop",
            "add": '<i class="fas fa-store" style="color:#006300"></i>',
            "remove": '<i class="fas fa-store-slash" style="color:grey"></i>'
        },
        plan: {
            "button_id": "sub_plan",
            "add": '<i class="far fa-calendar-check" style="color:#006300"></i>',
            "remove": '<i class="far fa-calendar-times" style="color:grey"></i>'
        }
    };
    
    let action = symbols_dict[button_type]
    console.log(button_type)
    $.ajax({
        type: "POST",
        url: endpoint,
        data:{
            recipe_id: recipe_id, 
            'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val(),
            tag: button_type,
            user_id: user_id
        },
        datatype:'json',
        success: function(data) {
            if (data['success']) {
                icon = document.getElementById(action['button_id'] + "_" + button_recipe);
                if (data['action'] == "add") {
                    icon.innerHTML = action['add'];
                }
                else if (data['action'] == 'remove') {
                    icon.innerHTML = action['remove'];
                }
            }
        }
    }); 
};

$(function(){ // this will be called when the DOM is ready
    let forms = document.getElementsByTagName('form');
    let length = forms.length

    for (i=0; i<length; i++) {
        let form_id = forms.item(i).id;
        let button_code = form_id.slice(0, 4);

        let button_type = undefined;
        let button_recipe = form_id.slice(5);

        if (button_code == "shop"){
            button_type = "shop";
        } else if (button_code == "plan") {
            button_type = "plan";
        } else if (button_code == "favt") {
            button_type = "favorite";
        }
        
        if (button_type != undefined) {
            forms.item(i).addEventListener("submit", function(evt){
                record_button(evt, button_type, button_recipe);    
            });
        }
    };
});