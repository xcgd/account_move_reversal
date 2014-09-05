from openerp import pooler


def call_post_function(cr, uid, context):
    __call_fct(cr, uid, context, 'post_function_')


def call_post_err_function(cr, uid, context):
    __call_fct(cr, uid, context, 'post_err_function_')


def __call_fct(cr, uid, context, context_key):
    """This functionality allows users of module account.move.reversal
      to call a function of the desired openerp model, after the
      reversal of the move.
    The call automatically sends at least the database cursor (cr) and
      the user id (uid) for security reasons.
    Two key parameters are required in the context to do so:
        - 'post_function_obj': the osv model where the function is defined,
        - 'post_function_name': the name of the function to call,
    And two optional key parameters:
        - 'post_function_args': an iterable object listing the required
            arguments to pass after 'cr, uid',
        - 'post_function_kwargs': a dictionary object listing the
            optionnal keyword args to pass.
    """

    obj_key = context_key + 'obj'

    if obj_key in context:
        name_key = context_key + 'name'
        args_key = context_key + 'args'
        kwargs_key = context_key + 'kwargs'

        # We get the function addr by its name,
        # and call it with (cr, uid, *args, **kwargs)
        getattr(
            pooler.get_pool(cr.dbname)[context[obj_key]],
            context[name_key]
        )(
            cr, uid,
            *context.get(args_key, []),
            **context.get(kwargs_key, {})
        )
        # We clean the context to avoid multiple calls of the function.
        context.pop(obj_key, None)
        context.pop(name_key, None)
        context.pop(args_key, None)
        context.pop(kwargs_key, None)
