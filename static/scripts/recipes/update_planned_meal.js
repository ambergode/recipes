function set_listeners() {
    let choices = document.getElementsByName('choose_food');
    let length = choices.length
    let plan_id = $('#plan_id').val();

    for (i=0; i<length; i++) {
        let choice_id = choices.item(i).id;

        choices.item(i).addEventListener("click", function(evt){
            record_choice(evt, plan_id, choice_id, undefined);    
        });
    }

    let servings = document.getElementsByName('meal_servings')
    length = servings.length
    for (i=0; i<length; i++) {
        let serving_id = servings.item(i).id;
        servings.item(i).addEventListener("change", function(evt){
            record_choice(evt, plan_id, undefined, serving_id);    
        });
    }
}

function record_choice(evt, plan_id, choice_id = undefined, serving_id = undefined) {
    evt.preventDefault(); 
    const endpoint = '/recipes/record_planned_meal/';

    let day = undefined
    let meal = undefined
    let food_type = undefined
    let food_id = undefined
    let servings = undefined

    if (choice_id != undefined ) {
        // parse the meaning of the id
        day = choice_id.slice(0, 3);
        food_type = choice_id.slice(10, 13);
        food_id = choice_id.slice(4, 9);
        meal = choice_id.slice(14);
    }

    if (serving_id != undefined) {
        day = serving_id.slice(0, 3)
        meal = serving_id.slice(4)
        servings = document.getElementById(serving_id).value
    }

    let replace_div_id = '#replaceable-content-' + day
    let replace_div = $(replace_div_id)

    let meal_id_id = '#id_' + day + '_' + meal
    let meal_id = $('#id_' + day + '_' + meal).val()
    console.log(meal, meal_id_id, meal_id)

    let data = {
        plan_id: plan_id, 
        'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val(),
        day: day,    
        meal: meal,
        food_type: food_type,
        food_id: food_id,
        servings: servings,
        meal_id: meal_id,
    }

    $.ajax({
        type: "POST",
        url: endpoint,
        data: data,
        datatype:'json',
        success: function(data) {
            if (data['success']) {
                if (data['html_from_view']) {
                    let html_from_view = data['html_from_view']
                    reload_partial_page(html_from_view, replace_div);
                    set_listeners()
                }
            }
        }
    }); 
};


$(function(){ // this will be called when the DOM is ready
    set_listeners()    
});