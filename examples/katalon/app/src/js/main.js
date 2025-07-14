var path = window.location.pathname;
var parts = path.split('/');
var pageId;
while ((pageId = parts.pop()) === '/') {
    continue;
}
window.pageId = pageId;
console.log(window.pageId);

require('jquery');
require('jquery-validation');
require('jquery-ui-dist/jquery-ui');
require('bootstrap-datepicker');
require('../js/form.js'); 