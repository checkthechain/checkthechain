from __future__ import annotations

import typing

from . import optimize_exceptions


async def async_bisect(
    async_f: typing.Callable[
        ...,
        typing.Coroutine[typing.Any, typing.Any, float],
    ],
    *,
    a: int | float,
    b: int | float,
    input_tol: float | None = None,
    output_tol: float | None = None,
    max_iterations: int | None = None,
    f_args: typing.Sequence[typing.Any] | None = None,
    f_kwargs: typing.Mapping[str, typing.Any] | None = None,
    verbose: bool = False,
) -> float:
    import asyncio

    # ensure that bounds are valid
    if a > b:
        raise optimize_exceptions.BadSearchDomain(
            'a must be less than b (' + str(a) + ' >= ' + str(b) + ')'
        )

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

    if verbose:
        print('probing min: f(' + str(a) + ') = ' + str(f_a))
        print('probing max: f(' + str(b) + ') = ' + str(f_b))

    # check if solution on boundary
    if f_a == 0:
        return a
    if f_b == 0:
        return b

    # check that function has opposite signs at bounds
    if (f_a < 0 and f_b < 0) or (f_a > 0 and f_b > 0):
        raise optimize_exceptions.BadSearchDomain(
            'function must have opposite signs at bounds, have:\n    f(a) = '
            + str(f_a)
            + '\n    f(b) = '
            + str(f_b)
        )

    iteration = 0
    while True:

        # compute c at midpoint
        c = (a + b) / 2
        f_c = await async_f(c, *f_args, **f_kwargs)

        if verbose:
            print('probing:   f(' + str(c) + ') = ' + str(f_c))

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
        summary = '\n'
        summary += 'found solution ' + str(c)
        summary += '\n- iterations = ' + str(iteration + 1)
        if input_tol is not None:
            summary += (
                '\n- input_precision = '
                + str((b - a) / 2)
                + ' < '
                + str(input_tol)
                + ' = input_tol'
            )
        if output_tol is not None:
            summary += (
                '\n- output_precision = '
                + str(abs(f_c))
                + ' < '
                + str(input_tol)
                + ' = output_tol'
            )
        print(summary)

    return c
