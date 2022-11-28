from __future__ import annotations

import math
import typing

import toolcli

import ctc.config
from ctc.config import config_defaults
from ctc import cli

if typing.TYPE_CHECKING:
    import toolstr


def _get_possible_charsets() -> typing.Sequence[str]:
    return [
        'whole',
        'quadrants',
        'sextants',
        'braille',
        'braille_bold',
    ]


def preview_available_charsets() -> None:
    import toolstr

    styles = cli.get_cli_styles()
    terminal_width = toolcli.get_n_terminal_cols()
    terminal_height = toolcli.get_n_terminal_rows()

    rows = []
    for charset in _get_possible_charsets():

        row: typing.MutableSequence[typing.Any] = []

        charset_mode, bold = _parse_charset_bold(charset)

        styled_charset = toolstr.add_style(
            charset,
            styles['description'] + ' bold',
        )
        row = [styled_charset]

        # 5 charsets, 3 lines for axis, 1 line for row separator
        n_rows = math.floor(terminal_height / 5) - 4
        n_rows = max(n_rows, 7)

        # 12 chars for names, 3 chars for gap, 5 chars for y axis
        charwidth = 12
        n_columns = terminal_width - charwidth - 3 - 5
        n_columns = min(n_columns, 200)

        example = _get_example_chart(
            charset_mode,
            bold=bold,
            n_rows=n_rows,
            n_columns=n_columns,
        )
        row.append(example)

        rows.append(row)

    toolstr.print_multiline_table(
        rows=rows,
        border='#555555',
        outer_gap=False,
        label_style=styles['title'],
        compact=3,
        justify='center',
    )


def print_current_charset() -> None:
    print(ctc.config.get_cli_chart_charset())


def set_charset(charset: str) -> None:
    import json

    if charset not in _get_possible_charsets():
        raise Exception('charset not recognized')

    config_path = ctc.config.get_config_path()
    with open(config_path, 'r') as f:
        config_data = json.load(f)
    new_config_data = dict(config_data, cli_chart_charset=charset)
    with open(config_path, 'w') as f:
        json.dump(new_config_data, f)
    print('charset updated')


def reset_charset() -> None:
    default = config_defaults.get_default_cli_chart_charset()
    set_charset(default)


def _get_example_chart(
    charset: toolstr.SampleMode,
    *,
    bold: bool,
    n_rows: int,
    n_columns: int,
) -> str:

    import toolstr

    xvals = [
        1663549798,
        1663567743,
        1663585761,
        1663603769,
        1663621776,
        1663639789,
        1663657809,
        1663675761,
        1663693762,
        1663711827,
        1663729797,
        1663747935,
        1663765760,
        1663783790,
        1663801774,
        1663819760,
        1663838132,
        1663855795,
        1663873797,
        1663891813,
        1663909792,
        1663927776,
        1663945815,
        1663963847,
        1663981781,
        1663999798,
        1664017853,
        1664035835,
        1664053867,
        1664071830,
        1664089840,
        1664107798,
        1664125763,
        1664143789,
        1664161760,
        1664179767,
        1664197774,
        1664215792,
        1664233778,
        1664251793,
        1664269891,
        1664287781,
        1664305781,
        1664323802,
        1664341783,
        1664359823,
        1664377802,
        1664395840,
        1664413967,
        1664431809,
        1664449803,
        1664467781,
        1664485791,
        1664503788,
        1664521788,
        1664539803,
        1664557813,
        1664575778,
        1664593781,
        1664611775,
        1664629794,
        1664647806,
        1664665786,
        1664683765,
        1664701964,
        1664719768,
        1664737794,
        1664755818,
        1664773796,
        1664791787,
        1664809793,
        1664827798,
        1664845831,
        1664863947,
        1664881902,
        1664900013,
        1664921344,
        1664940344,
        1664957356,
        1664975347,
        1664993349,
        1665011427,
        1665029480,
        1665047644,
        1665065432,
        1665083477,
        1665101506,
        1665119765,
        1665137780,
        1665155385,
        1665212696,
        1665230970,
        1665248995,
        1665267027,
        1665284972,
        1665303024,
        1665321073,
        1665338535,
        1665357452,
        1665375402,
        1665393623,
        1665411434,
        1665429449,
        1665447455,
        1665465462,
        1665483651,
        1665501440,
        1665519440,
        1665537435,
        1665555531,
        1665573487,
        1665591523,
        1665609468,
        1665627024,
        1665645128,
        1665663703,
        1665681487,
        1665699540,
        1665717473,
        1665735448,
        1665753540,
        1665771590,
        1665789433,
        1665807534,
        1665825745,
        1665843476,
        1665861498,
        1665879451,
        1665897447,
        1665915422,
        1665933470,
        1665951492,
        1665969451,
        1665987395,
        1666005538,
        1666023392,
        1666041387,
        1666059408,
        1666077332,
        1666095020,
        1666113010,
        1666131013,
    ]
    yvals = [
        3467676,
        3453030,
        3454119,
        3796471,
        2811590,
        2583242,
        2540971,
        2393300,
        2118438,
        2167304,
        2250817,
        2322956,
        2632182,
        1991117,
        3135101,
        3168271,
        3130747,
        2746798,
        3118622,
        3304237,
        3186955,
        4737040,
        4750685,
        4082261,
        3739130,
        3823873,
        2180280,
        2230629,
        2015357,
        1977475,
        1725739,
        1768291,
        1533972,
        1558876,
        1559917,
        1588033,
        1683268,
        1584899,
        1839346,
        2673650,
        2760701,
        2802530,
        4469266,
        6497735,
        6475775,
        6667969,
        6845996,
        3862950,
        3302120,
        2438624,
        2192687,
        1948085,
        1854789,
        1951629,
        1793283,
        1895097,
        1894419,
        1780919,
        1654981,
        1508337,
        1446603,
        1340254,
        1419903,
        1420392,
        1418633,
        1505979,
        1524823,
        1516790,
        1532488,
        1478960,
        1576259,
        1607261,
        1589575,
        1615215,
        1948395,
        1906605,
        1843213,
        2322029,
        2773918,
        2769934,
        2963073,
        2976986,
        2036006,
        1995463,
        1677147,
        1665046,
        1682327,
        1537053,
        1569590,
        1570455,
        5929404,
        6001726,
        3454068,
        1872224,
        1753042,
        1706135,
        1783495,
        1761368,
        1813299,
        1827998,
        1828796,
        1853029,
        1849574,
        1878760,
        1947701,
        1959216,
        1827818,
        1887162,
        1887540,
        1791694,
        1892058,
        2141942,
        2097121,
        2191771,
        2405314,
        2972825,
        3200850,
        3278544,
        3319151,
        2700243,
        2178400,
        1982263,
        1951093,
        2221039,
        2213348,
        2232286,
        2331262,
        2109742,
        2134551,
        2165043,
        2274100,
        2398506,
        2429913,
        2306730,
        2179818,
        2154776,
        3123419,
        3254481,
        3121522,
        3192413,
        3103306,
        2155926,
    ]

    styles = cli.get_cli_styles()
    if bold:
        line_style = styles['description'] + ' bold'
    else:
        line_style = styles['description']

    plot = toolstr.render_line_plot(
        xvals=xvals,
        yvals=yvals,
        n_rows=n_rows,
        n_columns=n_columns,
        line_style=line_style,
        chrome_style=styles['comment'],
        tick_label_style=styles['metavar'],
        yaxis_kwargs={'tick_label_format': {'prefix': '$', 'decimals': 0}},
        char_dict=charset,
        y_axis_width=5,
    )

    return plot


def _parse_charset_bold(charset: str) -> tuple[toolstr.SampleMode, bool]:
    if charset.endswith('_bold'):
        return charset[:-5], True  # type: ignore
    else:
        return charset, False  # type: ignore
