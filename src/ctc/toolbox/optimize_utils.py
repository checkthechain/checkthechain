import asyncio


async def async_bisect(
    async_f,
    a,
    b,
    input_tol=None,
    output_tol=None,
    max_iterations=None,
    f_args=None,
    f_kwargs=None,
    verbose=False,
):

    # ensure that bounds are valid
    if a > b:
        raise Exception('a must be less than b')

    # set defaults
    if f_args is None:
        f_args = []
    if f_kwargs is None:
        f_kwargs = {}

    # compute values on bounds
    f_a, f_b = await asyncio.gather(
        async_f(a, *f_args, **f_kwargs),
        async_f(b, *f_args, **f_kwargs),
    )

    # check if solution on boundary
    if f_a == 0:
        return a
    if f_b == 0:
        return b

    # check that function has opposite signs at bounds
    if (f_a < 0 and f_b < 0) or (f_a > 0 and f_b > 0):
        raise Exception('function must have opposite signs at bounds')

    iteration = 0
    while True:

        # compute c at midpoint
        c = (a + b) / 2
        f_c = await async_f(c, *f_args, **f_kwargs)

        if verbose:
            print('probing input=' + str(c) + ', f(input)=' + str(f_c))

        # check if solution found
        if f_c == 0:
            break
        if input_tol is not None:
            input_tol_satisfied = (b - a) / 2 < input_tol
        else:
            input_tol_satisfied = True
        if output_tol is not None:
            output_tol_satisfied = abs(f_c) < output_tol
        else:
            output_tol_satisfied = True
        if input_tol_satisfied and output_tol_satisfied:
            break

        # check whether to update a or b
        if (f_c > 0) == (f_a > 0):
            a = c
            f_a = f_c
        else:
            b = c
            f_b = f_c

        if verbose:
            print('new range:', [a, b])

        iteration += 1
        if max_iterations is not None and iteration >= max_iterations:
            raise Exception('solution could not be found')

    if verbose:
        print('found solution ' + str(c))

    return c

