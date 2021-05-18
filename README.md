# recipes

This is an app to keep track of one's favorite recipes.


Things to credit:
    favicon: 
    <div>Onion icon made by <a href="https://www.freepik.com" title="Freepik">Freepik</a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com</a></div>

    https://openfolder.sh/django-tutorial-as-you-type-search-with-ajax for explaining ajax and a lot of code

    https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Authentication
    for explaining a walkthrough of Django authentication

    Food Data Central
    https://fdc.nal.usda.gov/
    for the database from which I loaded mine

    W3 schools
    StackExchange
    GeeksForGeeks
    Django

    FontAwesome for icons


TODO:
- register
- Toggle on navbar not working
- On shopping list page: add button to switch types of units (metric to imperial)
- switch search on index to ajax
- Add nutrition info to detail page (maybe some to main page)
- Add "create regular shopping list" page
- on index: buttons to display all public recipes, personal recipes, favorites
- detail page - multiply recipe - and have that go to shopping list
- put multiply recipe on card as well (instead of add to list? # in list: default 0)
- if 0 as quantity in recipe: ask user if actually desired
- add data validation to all forms
- make cards fill all possible space - turn direction to cols instead of rows? masonry through javascript?
- add recipe circles so users can share recipes with a group (upper level function: be part of mulitple groups)
- prefill category and unit forms for add_ingredient edit recipe version
- update navbar to include create recipe, reorganize links
- make modal to edit ingredient take up more width - no long indent (add wrapping div for adding new ingredient with class = indented)
- Figure out why so many ingredients have "undetermined" as their common serving size unit