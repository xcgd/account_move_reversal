from openerp import pooler


def call_post_function(cr, uid, context):
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

    if 'post_function_obj' in context:
        # We get the function addr by its name,
        # and call it with (cr, uid, *args, **kwargs)
        getattr(
            pooler.get_pool(cr.dbname)[context['post_function_obj']],
            context['post_function_name']
        )(
            cr, uid,
            *context['post_function_args'],
            **context['post_function_kwargs']
        )
        # We clean the context to avoid multiple calls of the function.
        del context['post_function_obj']
        del context['post_function_name']
        del context['post_function_args']
        del context['post_function_kwargs']
