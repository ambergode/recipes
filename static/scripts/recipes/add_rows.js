// adds rows to the end of a form when data entered into last row

$(function(){ // this will be called when the DOM is ready
    let step_list = document.getElementById("step_list")
    if (step_list != null) {
        step_list.onchange = function () {
    
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
    };
});