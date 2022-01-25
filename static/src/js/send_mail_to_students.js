odoo.define("courses.ListStudentsInCourse", function (require) {
    "use strict";

    var publicWidget = require("web.public.widget");

    publicWidget.registry.ListStudentsInCourse = publicWidget.Widget.extend({
        selector: ".Send_mail_to_students",
        events: _.extend({}, publicWidget.Widget.prototype.events, {
            'click #sendMailToStudents': 'sendMailToStudents',
        }),

        sendMailToStudents: function (){
            console.log("Marko");
        },
    });
});