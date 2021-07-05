function fetch_call() {
    
    // start animating the search icon with the CSS class
    $('#search-icon').addClass('blink')
    
    const csrftoken = Cookies.get('csrftoken');

    // determine function for fetch to run
    const curr_pathname = window.location.pathname;
    const edit_regex = /\/recipes\/([0-9]+)\/edit\//
    const edit_found = curr_pathname.match(edit_regex);
    const list_regex = /\/recipes\/([0-9]+)\/update_shopping_list\//
    const list_found = curr_pathname.match(list_regex);

    let path = '/recipes/'
    if (edit_found || list_found) {
        path = curr_pathname
    }

    const user_input = document.querySelector('#user-input').value
    let selectedValue = undefined;
    const radios = document.querySelectorAll('input[name="group"]')
    radios.forEach(radio => {
        if (radio.checked) {
            selectedValue = radio.value;
        }
    })

    fetch(path, {
        method: 'POST',
        body: JSON.stringify({
            q: user_input,
            radio: selectedValue,
            endpoint: window.location.pathname    
        }),
        headers: {
            "X-Requested-With": "XMLHttpRequest",
            'X-CSRFToken': csrftoken
        },
        credentials: 'same-origin'
    })
    .then(response => response.json())
    .then(response => {
        const reload_div = $('#replaceable-content');
        reload_partial_page(response['html_from_view'], reload_div, listeners = ['buttons', 'edit_ing', 'add_ing'])
    });
}


function reload_partial_page(html_from_view, reload_div, listeners = undefined) {

    // fade out the ing_div, then:
    reload_div.fadeTo('fast', 0).promise().then(() => {
        // replace the HTML contents
        reload_div.html(html_from_view)
        // fade-in the div with new contents
        reload_div.fadeTo('fast', 1)
        if (document.querySelector('#search-icon') && document.querySelector('#search-icon').classList.contains('blink')) {
            // stop animating search icon
            $('#search-icon').removeClass('blink')
        }

        if (listeners && listeners.includes('buttons')) {
            // reset listeners for the buttons
            set_button_listeners()
        }

        if (listeners && listeners.includes('edit_ing')) {
            set_edit_ing_listeners()
        }

        if (listeners && listeners.includes('add_ing')) {
            document.querySelector('#add_to_recipe').addEventListener('click', (evt) =>{
                add_ingredient(evt)
                document.querySelector("#user-input").value = ''   
                document.querySelector('#replaceable-content').innerHTML=""
            })
        }

        return false;
    })
}


function add_ingredient(evt) {
    evt.preventDefault();
    const csrftoken = Cookies.get('csrftoken');

    let ingredient_id = document.getElementById('ingredient_name').value    
    let model = document.querySelector('#model').value

    fetch('add_ing_to_list/', {
        method: 'POST',
        body: JSON.stringify({
            ingredient_id: ingredient_id,  
            model: model,  
        }),
        headers: {
            "X-Requested-With": "XMLHttpRequest",
            'X-CSRFToken': csrftoken
        },
        credentials: 'same-origin'
    })
    .then(response => response.json())
    .then(response => {
        const reload_div = $('#ingredients_list');
        reload_partial_page(response['html_from_view'], reload_div, listeners = ['edit_ing'])
    });
}


function record_button (evt, button_type, button_recipe, source) {
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

    // complete fetch call to let server know of change
    const csrftoken = Cookies.get('csrftoken');
    const body = {
        recipe_id: recipe_id, 
        tag: button_type,
        model: model,
        source: source,
    }
    
    fetch(endpoint, {
        method: 'POST',
        body: JSON.stringify(body),
        headers: {
            "X-Requested-With": "XMLHttpRequest",
            'X-CSRFToken': csrftoken
        },
        credentials: 'same-origin'
    })
    .then(response => response.json())
    .then(data => {
        icon = document.getElementById(action['button_id'] + "_" + button_recipe);
        if (data['action'] == "add") {
            icon.innerHTML = action['add'];
        }
        else if (data['action'] == 'remove') {
            icon.innerHTML = action['remove'];
        }
        if (data['html_from_view']) {
            let html_from_view = data['html_from_view']
            reload_partial_page(html_from_view, $('#replaceable-content'));
        }
    }); 
};


function set_button_listeners() {
    let forms = document.querySelectorAll('form');
    forms.forEach(form => {

        let form_id = form.id;
        let button_recipe = form_id.slice(5);

        // determine type of button
        let button_code = form_id.slice(0, 4);
        let button_type = undefined;
        if (button_code == "shop"){
            button_type = "shop";
        } else if (button_code == "plan") {
            button_type = "plan";
        } else if (button_code == "favt") {
            button_type = "favorite";
        }

        let source = undefined;
        if (window.location.pathname === '/recipes/shoppinglist/') {
            source = 'shopping'
        }

        if (button_type != undefined) {
            form.addEventListener("submit", function(evt){
                record_button(evt, button_type, button_recipe, source);    
            });
        }
    })
}


function update_ingredients (evt, button_type, button_ingquant) {
    
    if (button_type === 'rem') {
        evt.preventDefault()
        swal({
            title: "Are you sure that you want to delete this ingredient?",
            icon: "warning",
            buttons: true,
            dangerMode: true,
        })
        .then(willDelete => {
            if (willDelete) {
                update_ingredients_helper ({
                    tag: button_type,
                    ingquant_id: button_ingquant
                })
            }
        });
    } else {
        evt.preventDefault()
        body = {
            tag: button_type,
            ingquant_id: button_ingquant,
            ing_category: document.querySelector('#category_' + button_ingquant).value,
            serving_size: document.querySelector('#serving_size_' + button_ingquant).value,
            serving_unit: document.querySelector('#serving_unit_' + button_ingquant).value,
            weight: document.querySelector('#weight_' + button_ingquant).value,
            calories: document.querySelector('#calories_' + button_ingquant).value,
            fat: document.querySelector('#fat_' + button_ingquant).value,
            transfat: document.querySelector('#transfat_' + button_ingquant).value,
            satfat: document.querySelector('#satfat_' + button_ingquant).value,
            polyunsatfat: document.querySelector('#polyunsatfat_' + button_ingquant).value,
            monounsatfat: document.querySelector('#monounsatfat_' + button_ingquant).value,
            cholesterol: document.querySelector('#cholesterol_' + button_ingquant).value,
            sodium: document.querySelector('#sodium_' + button_ingquant).value,
            carbs: document.querySelector('#carbs_' + button_ingquant).value,
            fiber: document.querySelector('#fiber_' + button_ingquant).value,
            sugar: document.querySelector('#sugar_' + button_ingquant).value,
            protein: document.querySelector('#protein_' + button_ingquant).value,
        }
        update_ingredients_helper(body)
        $('#modal_' + button_ingquant).modal('hide')
    }

    function update_ingredients_helper(body) {
        const endpoint = "/recipes/update_ingredients/";

        // complete fetch call to let server know of change
        const csrftoken = Cookies.get('csrftoken');

        fetch(endpoint, {
            method: 'POST',
            body: JSON.stringify(body),
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                'X-CSRFToken': csrftoken
            },
            credentials: 'same-origin'
        })
        .then(response => response.json())
        .then(data => {
            reload_partial_page(data['html_from_view'], $('#ingredients_list'), listeners = 'edit_ing')              
        })
    }
    
} 


function set_edit_ing_listeners() {
    let buttons = document.querySelectorAll('button');
    buttons.forEach(button => {
        // determine type of buttons
        let button_id = button.id;
        let button_type = button_id.slice(0, 3);
        // get the id of the ingquant to deal with
        let button_ingquant = button_id.slice(4);

        // if buttons are edit or remove, add an event listener
        if (button_type == 'edt' || button_type == "rem") {
            button.addEventListener("click", function (evt) {
                update_ingredients(evt, button_type, button_ingquant)
            });    
        }
    })

    let delete_buttons = document.querySelectorAll('button[name="delete_ingredient"]')
    delete_buttons.forEach(button => {
        button.addEventListener("click", function(evt) {
            evt.preventDefault();
            swal({
                title: "Permanently delete?",
                text: "Are you sure that you want to permanently delete this ingredient? You won't be able to use it in any other recipes and it will disappear from any recipes it is already part of.",
                icon: "warning",
                buttons: true,
                dangerMode: true,
            })
            .then(willDelete => {
                if (willDelete) {
                    const endpoint = "delete_ing/";

                    // complete fetch call to let server know of change
                    const csrftoken = Cookies.get('csrftoken');
                    fetch(endpoint, {
                        method: 'POST',
                        body: JSON.stringify({
                            ing_id: this.id.slice(18),
                            model: $('#model').val(),
                        }),
                        headers: {
                            "X-Requested-With": "XMLHttpRequest",
                            'X-CSRFToken': csrftoken
                        },
                        credentials: 'same-origin'
                    })
                    .then(response => response.json())
                    .then(data => {
                        reload_partial_page(data['html_from_view'], $('#ingredients_list'), listeners = 'edit_ing')   
                        $(`#${this.value}`).modal('hide')          
                    })
                    return false
                }
            }); 
        });    
    })
}


function add_rows(step_list) {
    // keep track of how many steps there are and what order they go in
    number_li = step_list.children.length;
    human_read_num = number_li + 1;

    let counter = document.getElementById("num_steps");
    counter.value = human_read_num;
    
    let step_name = "step_" + (number_li - 1).toString()
    let last_input = document.getElementById(step_name);
    if (last_input != null && last_input.value != "") {
        // create a new form input for the next step
        let new_div = document.createElement("div");
        new_div.setAttribute('class', 'row');
        let next_div = document.createElement('div');
        next_div.setAttribute('class', 'col g-1');
        let li = document.createElement('li');
        let node = document.createElement("input");
        node.setAttribute("name", "step_" + number_li);
        node.setAttribute("type", "text");
        node.setAttribute("class", "full-width");
        node.setAttribute("class", "form-control");
        let node_name = "step_" + number_li;
        node.setAttribute("id", node_name);
        node.setAttribute("value", "")

        // add the new input into the li and then the ul
        li.appendChild(node);
        next_div.appendChild(li);
        new_div.appendChild(next_div);

        step_list.appendChild(new_div);

        // autofocus into new textbox
        document.getElementById(node_name).focus();
    }
};


function set_enddate(startdate, num_days) {
    let enddate = new Date(startdate)
    enddate.setDate(enddate.getDate() + num_days)

    // write the new date into the html
    const enddate_div = document.querySelector('#enddate')
    let month = enddate.getMonth() + 1
    if (month < 10) {
        month = `0${String(month)}`
    }
    let day = enddate.getDate()
    if (day <10) {
        day = `0${String(day)}`
    }
    enddate_div.value = `${enddate.getFullYear()}-${month}-${day}`

    let plan_container = document.querySelector('#plan-container')
    if (plan_container) {
        console.log('true')
        update_days()
    } 
}


function set_days() {
    let enddate = new Date(document.querySelector('#enddate').value +' 12:00:00')
    let startdate = new Date(document.querySelector('#startdate').value + ' 12:00:00')
    let delta = (enddate - startdate)/(1000 * 60 * 60 * 24)

    if (delta > 14) {
        swal({
            text: 'It is not recommended to have plan that lasts more than 14 days.'
        })
        days.value = (enddate - startdate)/(1000 * 60 * 60 * 24)
    } else if (delta > 0) {
        days.value = (enddate - startdate)/(1000 * 60 * 60 * 24)
    } else {
        swal({
            text: 'Please enter a date after the startdate.'
        })
    }

    let plan_container = document.querySelector('#plan-container')
    if (plan_container) {
        console.log('true')
        update_days()
    } 
}


function update_days() {
    const csrftoken = Cookies.get('csrftoken');
    fetch('update_days/', {
        method: 'POST',
        body: JSON.stringify({
           startdate: document.querySelector('#startdate').value,
           enddate: document.querySelector('#enddate').value,
        }),
        headers: {
            "X-Requested-With": "XMLHttpRequest",
            'X-CSRFToken': csrftoken
        },
        credentials: 'same-origin'
    })
    .then(response => response.json())
    .then(response => {
        console.log(response)
    });
}


function list_fetch_call(body, day_meal) {
    
    const csrftoken = Cookies.get('csrftoken');
    fetch('list_recipes/', {
        method: 'POST',
        body: JSON.stringify(body),
        headers: {
            "X-Requested-With": "XMLHttpRequest",
            'X-CSRFToken': csrftoken
        },
        credentials: 'same-origin'
    })
    .then(response => response.json())
    .then(response => {
        // display new list
        document.querySelector('#replaceable-content_' + day_meal).innerHTML = response['html_from_view']

        // set listeners for clicking on an option
        inputs = document.querySelectorAll('.recipe_option')
        inputs.forEach(item => {
            item.addEventListener('click', function() {
                record_plan_selection(day_meal.slice(0,3), day_meal.slice(4), item.id)
            })
        })  
    });
}


function record_plan_selection(day, meal, recipe_id) {
    const csrftoken = Cookies.get('csrftoken');
    fetch('add_recipe/', {
        method: 'POST',
        body: JSON.stringify({
            day: day,
            meal: meal, 
            recipe_id: recipe_id,
            add_or_remove: 'add'
        }),
        headers: {
            "X-Requested-With": "XMLHttpRequest",
            'X-CSRFToken': csrftoken
        },
        credentials: 'same-origin'
    })
    .then(response => response.json())
    .then(response => {
        close_lists()
        let food_list = $('#planned_food_' + day + '_' + meal)
        reload_partial_page(response['html_from_view'], food_list, listeners = undefined)
    })
}


function close_lists() {
    // close all other lists
    var open_lists = document.querySelectorAll(".recipe_option");
    if (open_lists) {
        open_lists.forEach(item => {
            item.parentNode.removeChild(item)
        })
    }
}


function remove_food(day, meal, recipe_id) {
    const csrftoken = Cookies.get('csrftoken');
    fetch('add_recipe/', {
        method: 'POST',
        body: JSON.stringify({
            day: day,
            meal: meal,
            recipe_id: recipe_id,
            add_or_remove: 'remove'
        }),
        headers: {
            "X-Requested-With": "XMLHttpRequest",
            'X-CSRFToken': csrftoken
        },
        credentials: 'same-origin'
    })
    .then(response => response.json())
    .then(response => {
        close_lists()
        let food_list = $('#planned_food_' + day.padStart(3, '0') + '_' + meal)
        reload_partial_page(response['html_from_view'], food_list, listeners = undefined)
    })
}


function add_note(day, meal) {
    // display the note box
    note_div = $("#replaceable_notes_" + day.padStart(3, '0') + "_" + meal)
    reload_partial_page(
        `<div class='row g-1'>
            <div class='col'>
                Notes: 
                <input type='text' name='notes_${day.padStart(3, '0')}_${meal}' id='notes_${day.padStart(3, '0')}_${meal}' class='form-control' placeholder='additional notes' autocomplete="off"></input>
            </div>
        </div>`,
        note_div, 
        listeners = undefined 
    )
    icon = document.querySelector(`#add_notes_${day.padStart(3, "0")}_${meal}`)
    icon.parentNode.remove(icon)
}


function add_rem_meal(day, meal, action) {

    if (meal === 'day') {
        swal({
            title: "Are you sure that you want to delete this day?",
            icon: "warning",
            buttons: true,
            dangerMode: true,
        })
        .then(willDelete => {
            if (!willDelete) {
                return false;
            } else {
                meal_helper(day, meal, action)
            }
        });
    } else {
        meal_helper(day, meal, action)
    }

    function meal_helper(day, meal, action) {
        let add_meal = false
        let remove_meal = false
        
        if (action === 'add') {
            add_meal = true
        } else if (action === 'rem') {
            remove_meal = true
        }
    
        const csrftoken = Cookies.get('csrftoken');
        fetch('update_plan_ajax/', {
            method: 'POST',
            body: JSON.stringify({
                add_meal: add_meal,
                remove_meal: remove_meal,
                day: day,
                meal: meal,
            }),
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                'X-CSRFToken': csrftoken
            },
            credentials: 'same-origin'
        })
        .then(response => response.json())
        .then(response => {
            let plan_card = $('#replaceable-content-' + day.padStart(3, '0'))
            reload_partial_page(response['html_from_view'], plan_card, listeners = undefined)
        })
    }
}


function update_ppl() {
    let peep_inputs = document.querySelectorAll('.peep-input')
    let original_ppl = this.dataset.original
    if (peep_inputs) {
        peep_inputs.forEach(peep_input => {
            if (peep_input.value === original_ppl) {
                peep_input.value = this.value
                this.dataset.original = this.value
            }
        })
    }
}


function update_meals() {
    const csrftoken = Cookies.get('csrftoken');
    fetch('add_base_meals/', {
        method: 'POST',
        body: JSON.stringify({
            meal: this.value,
            add: this.checked
        }),
        headers: {
            "X-Requested-With": "XMLHttpRequest",
            'X-CSRFToken': csrftoken
        },
        credentials: 'same-origin'
    })
    .then(response => response.json())
    .then(response => {
        let plan_container = $('#plan-container')
        reload_partial_page(response['html_from_view'], plan_container, listeners = undefined)
    })
}


function schedule_list_call_helper(input_html) {
    let day_meal = input_html.id.slice(7)            
    // if scheduled_function is NOT false, cancel the execution of the function
    if (scheduled_function) {
        clearTimeout(scheduled_function)
    }
    // setTimeout returns the ID of the function to be executed
    scheduled_function = setTimeout(list_fetch_call, 500, {
        q: input_html.value,
    }, day_meal)
}


// document.querySelector('form[name="edit_meal_plan"]').action = `update_and_edit_plan/`
// document.querySelector('#update_plan').click()

// global variable
let scheduled_function = false

$(function(){ // this will be called when the DOM is ready
    // start out with no scheduled functions
    

    // listen for search in user_input search bar
    $("#user-input").on('keyup', () => {
        // if scheduled_function is NOT false, cancel the execution of the function
        if (scheduled_function) {
            clearTimeout(scheduled_function)
        }
        // setTimeout returns the ID of the function to be executed
        scheduled_function = setTimeout(fetch_call, 500)
    })

    
    // listen for changes to radio buttons for search
    radios = document.querySelectorAll('input[name="group"]')
    radios.forEach(radio => {
        radio.addEventListener('click', () => {
            scheduled_function = schedule_function(scheduled_function)
        })
    })


    // listen for shopping, planning, and favorite changes
    set_button_listeners()

    const curr_pathname = window.location.pathname;
    const edit_regex = /\/recipes\/([0-9]+)\/edit\//
    const edit_found = curr_pathname.match(edit_regex);
    const list_regex = /\/recipes\/([0-9]+)\/update_shopping_list\//
    const list_found = curr_pathname.match(list_regex);
    // listen for edit or remove buttons on edit recipe page
    if (edit_found || list_found) {
        set_edit_ing_listeners()
    }

    // if there is a delete recipe button, listen for it and check if the user really wants to delete
    if (document.querySelector('#delete_recipe')) {
        document.querySelector('#delete_recipe').addEventListener('click', (evt) => {
            evt.preventDefault();
            swal({
                title: "Are you sure that you want to delete this recipe?",
                icon: "warning",
                buttons: true,
                dangerMode: true,
            })
            .then(willDelete => {
                if (willDelete) {
                    document.querySelector('#delete_recipe_form').submit();
                }
            });
        })
    }

    // if there is a step list, add a listener
    let step_list = document.getElementById("step_list")
    if (step_list != null) {
        step_list.addEventListener('change', function() {
            add_rows(this);
        })
    };

    const days = document.querySelector('#days')
    if (days) {
        let num_days = parseInt(days.value)
        const startdate_div = document.querySelector('#startdate')
        const startdate = new Date(startdate_div.value + ' 12:00:00')
        set_enddate(startdate, num_days)
        days.addEventListener('change', function() {
            num_days = parseInt(this.value)
            if (num_days > 14) {
                swal({
                    text: 'It is not recommended to have plan that lasts more than 14 days.'
                })
                set_enddate(startdate, num_days)
            } else if (num_days <= 0) {
                swal({
                    text: 'Please enter a positve number of days.'
                })
            } else {
                set_enddate(startdate, num_days)
            }
        })
    
        const enddate_div = document.querySelector('#enddate')
        enddate_div.addEventListener('change', () => {
            set_days()
        })
        startdate_div.addEventListener('change', () => {
            set_days() 
        })
    }

    // listen for clicks outside of input and close lists
    document.addEventListener('click', close_lists)
    
    // listen for changes to main plan
    const ppl = document.querySelector('#people')
    if (ppl) {
        ppl.addEventListener('change', update_ppl)
    }
    
    const meals = document.querySelectorAll('.meal_time_choices')
    meals.forEach(meal => {
        meal.addEventListener('change', update_meals)
    })
})