Introduction
============

Clients often want to be able to create templates for their forms. Let's say
the company conducts interviews for a large number of positions on a daily
basis. They want to be able to create an interview form for every position.
They would do this quite often because requirements change. It's not practical
to contact the application's developer to add/remove a field from a form each
time a requirement changes. This is where dynamic forms come in. 

Via the django admin interface, clients can create forms and insert into them
whatever fields they want, in whatever order. They can easily reorder
questions, change wording, etc. When the client's end users interact with the
application, they are presented with a simple HTML form. This form is submitted
and responses saved. Each form can be submitted multiple times - each response
to that interview form will then be saved into a 'bucket' of sorts that holds
all the responses that particular user submitted at that time. This is useful
if you are conducting a periodical survey.

Django dynamic forms comes as a reusable django app that you can easily drop
into your project.
