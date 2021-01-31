# pjobq architecture

As much as possible, we try to seperate state from logic.
In general dataclasses are preferred, with functions operating over them, instead of defining member funtions of a class.

# Points of interest
The following are important sections of the code:

[init_state](../pjobq/runtime/init_state.py)
This is where we specify the implementations of abstract classes, and populate a 'State' object with them.
Also perform startup logic here.

[bootstrap](../pjobq/bootstrap.py)
This defines most of what the runtime looks like.
