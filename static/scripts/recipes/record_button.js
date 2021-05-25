// This function based on https://morioh.com/p/560b11927857

function reload_shopping(html_from_view) {
    
    const endpoint = '/recipes/shoppinglist/'

    let ing_div = $('#replaceable-content');

    // fade out the ing_div, then:
    ing_div.fadeTo('fast', 0).promise().then(() => {
        // replace the HTML contents
        ing_div.html(html_from_view)
        // fade-in the div with new contents
        ing_div.fadeTo('fast', 1)

    })
}


function record_button (evt, button_type, button_recipe, source = undefined) {
    evt.preventDefault(); 
    const recipe_id = button_recipe;
    const endpoint = "/recipes/button_ajax/";
    const model = $('#model').val();
    let symbols_dict = {
        favorite: {
            "button_id": "sub_fav",
            "add": '<i class="fas fa-heart" title="Remove from Favorites" style="color:#ab0000"></i>',
            "remove": '<i class="far fa-heart" title="Add to Favorites" style="color:grey"></i>'
        },
        shop:{
            "button_id": "sub_shop",
            "add": '<i class="fas fa-store" title="Remove from Shopping List" style="color:#006300"></i>',
            "remove": '<i class="fas fa-store-slash" title="Add to Shopping List" style="color:grey"></i>'
        },
        plan: {
            "button_id": "sub_plan",
            "add": '<i class="far fa-calendar-check" title="Remove from Meal Planning" style="color:#006300"></i>',
            "remove": '<i class="far fa-calendar-times" title="Add to Meal Planning"style="color:grey"></i>'
        }
    };
    
    let action = symbols_dict[button_type]

    $.ajax({
        type: "POST",
        url: endpoint,
        data:{
            recipe_id: recipe_id, 
            'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val(),
            tag: button_type,
            model: model,
            source: source,
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
                if (data['html_from_view']) {
                    let html_from_view = data['html_from_view']
                    reload_shopping(html_from_view)
                }
            }
        }
    }); 
};

$(function(){ // this will be called when the DOM is ready
    let forms = document.getElementsByTagName('form');
    let length = forms.length
    let source = window.location.pathname

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
            if (source == '/recipes/shoppinglist/') {
                forms.item(i).addEventListener("submit", function(evt){
                    record_button(evt, button_type, button_recipe, source = 'shopping');    
                });
            } else {
                forms.item(i).addEventListener("submit", function(evt){
                    record_button(evt, button_type, button_recipe);    
                });
            }
            
        }
    };
});