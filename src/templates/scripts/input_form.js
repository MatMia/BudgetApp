const selectTypeElement = document.getElementById('expense_type');

$.ajax({
    url:"/input_category",
    type:"POST",
    data: selectTypeElement.value,
    success: function(data) {
    
    selectCategory = document.getElementById('expense_category');

    // Load the new options
    $.each(data, function(key, value) {
        selectCategory.options.add(new Option(key, key));
    });
}}
);

selectTypeElement.addEventListener('change', (event) => {
    $.ajax({
    url:"/input_category",
    type:"POST",
    data: selectTypeElement.value,
    success: function(data) {
    
    selectCategory = document.getElementById('expense_category');
    
    // Clear the old options
    selectCategory.options.length = 0;
    // Load the new options
    $.each(data, function(key, value) {
        selectCategory.options.add(new Option(key, key));
    });
}}
);
setTimeout(() => { 
$.ajax({
    url:"/input_sub_category",
    type:"POST",
    data: {category : selectCategory.value, type : selectTypeElement.value},
    success: function(data) {
    
    selectSubCategory = document.getElementById('expense_sub_category');
    
    // Clear the old options
    selectSubCategory.options.length = 0;
    // Load the new options
    $.each(data, function(key, value) {
        selectSubCategory.options.add(new Option(key, key));
    });
}});

}, "100")
})

var selectCategoryElement = document.getElementById('expense_category');
setTimeout(() => {

$.ajax({
    url:"/input_sub_category",
    type:"POST",
    data: {category : selectCategoryElement.value, type : selectTypeElement.value},
    success: function(data) {
    
    selectSubCategory = document.getElementById('expense_sub_category');

    // Load the new options
    $.each(data, function(key, value) {
        selectSubCategory.options.add(new Option(key, key));
    });
}}
)}, "100")

selectCategoryElement.addEventListener('change', (event) => {
    $.ajax({
    url:"/input_sub_category",
    type:"POST",
    data: {category : selectCategoryElement.value, type : selectTypeElement.value},
    success: function(data) {
    
    selectSubCategory = document.getElementById('expense_sub_category');
    
    // Clear the old options
    selectSubCategory.options.length = 0;
    // Load the new options
    $.each(data, function(key, value) {
        selectSubCategory.options.add(new Option(key, key));
    });
}}
);
})

$(document).ready(function(){
    var date_input=$('input[name="expense_date"]');
    var container=$('.bootstrap-iso form').length>0 ? $('.bootstrap-iso form').parent() : "body";
    var options={
      format: 'yyyy-mm-dd',
      container: container,
      todayHighlight: true,
      autoclose: true,
    };
    date_input.datepicker(options);
  })