// This code primarily thanks to:
// https://openfolder.sh/django-tutorial-as-you-type-search-with-ajax
$(function(){ // this will be called when the DOM is ready
    const user_input = $("#user-input")
    const search_icon = $('#search-icon')
    const recipe_id = $('#recipe_id').val()
    const endpoint = '/recipes/' + String(recipe_id) + '/edit/'
    const delay_by_in_ms = 700
    let scheduled_function = false
    
    
    let ajax_call = function (endpoint, request_parameters) {
        $.getJSON(endpoint, request_parameters)
            .done(response => {
                
                const num_ingredient_options = response['number_ingredients']
                console.log("this")
                let ing_div = undefined
                if (num_ingredient_options > 0) {
                    ing_div = $('#replaceable-content')
                } else {
                    ing_div = $('#replaceable-content-add-ing')
                }
                        
                // fade out the ing_div, then:
                ing_div.fadeTo('fast', 0).promise().then(() => {
                    // replace the HTML contents
                    ing_div.html(response['html_from_view'])
                    // fade-in the div with new contents
                    ing_div.fadeTo('fast', 1)
                    // stop animating search icon
                    search_icon.removeClass('blink')
                })
            })
    }


    user_input.on('keyup', function () {
        const request_parameters = {
            q: $(this).val().toLowerCase() // value of user_input: the HTML element with ID user-input
        }
        
        // start animating the search icon with the CSS class
        search_icon.addClass('blink')

        // if scheduled_function is NOT false, cancel the execution of the function
        if (scheduled_function) {
            clearTimeout(scheduled_function)
        }

        // setTimeout returns the ID of the function to be executed
        scheduled_function = setTimeout(ajax_call, delay_by_in_ms, endpoint, request_parameters)
    })
})