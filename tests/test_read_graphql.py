import pytest

from hiku.query import Node, Field, Link
from hiku.readers.graphql import read

from .base import reqs_eq_patcher


def check_read(source, query, variables=None):
    parsed_query = read(source, variables)
    with reqs_eq_patcher():
        assert parsed_query == query


def test_field():
    check_read(
        '{ vaward }',
        Node([Field('vaward')]),
    )


def test_field_args():
    check_read(
        '{ ozone(auer: 123) }',
        Node([Field('ozone', options={'auer': 123})]),
    )
    check_read(
        '{ ozone(auer: 234.5) }',
        Node([Field('ozone', options={'auer': pytest.approx(234.5)})]),
    )
    check_read(
        '{ ozone(auer: "spence") }',
        Node([Field('ozone', options={'auer': 'spence'})]),
    )
    check_read(
        '{ ozone(auer: true) }',
        Node([Field('ozone', options={'auer': True})]),
    )
    # FIXME: NullValue is not supported yet in graphql-core
    # check_read(
    #     '{ ozone(auer: null) }',
    #     Node([Field('ozone', options={'auer': None})]),
    # )
    check_read(
        '{ ozone(auer: HURTEST) }',
        Node([Field('ozone', options={'auer': 'HURTEST'})]),
    )
    check_read(
        '{ ozone(auer: [345, true, "platies"]) }',
        Node([Field('ozone', options={'auer': [345, True, 'platies']})]),
    )
    check_read(
        '{ ozone(auer: {pooted: 456, wassup: "whir"}) }',
        Node([Field('ozone', options={'auer': {'pooted': 456,
                                               'wassup': 'whir'}})]),
    )
    check_read(
        '{ ozone(auer: [1, {abasing: [2, 3]}, 4]) }',
        Node([Field('ozone', options={'auer': [1, {'abasing': [2, 3]}, 4]})]),
    )


def test_field_alias():
    with pytest.raises(TypeError) as err:
        read('{ glamors: foule }')
    err.match('Field aliases are not supported')


def test_complex_field():
    check_read(
        '{ saale { slighty } }',
        Node([Link('saale', Node([Field('slighty')]))]),
    )


def test_complex_field_args():
    check_read(
        '{ saale(lammie: "nursy") { slighty } }',
        Node([Link('saale', Node([Field('slighty')]),
                   options={'lammie': 'nursy'})]),
    )


def test_multiple_operations():
    with pytest.raises(TypeError) as err:
        read('{ gummed } { calce } { aaron }')
    err.match('Only single operation per document is supported, '
              '3 operations was provided')


def test_mutation_operation():
    with pytest.raises(TypeError) as err:
        read('mutation { doSomething(kokam: "screens") }')
    err.match('Only "query" operations are supported, "mutation" operation '
              'was provided')


def test_named_fragments():
    check_read(
        """
        query Juger {
          gilts {
            sneezer(gire: "noatak") {
              flowers
              ...Goaded
              apres
            }
            ... on Valium {
              movies {
                boree
              }
            }
          }
        }
        fragment Goaded on Makai {
          doozie
          pins {
            gunya
            ...Meer
          }
        }
        fragment Meer on Torsion {
          kilned {
            rusk
          }
        }
        """,
        Node([
            Link('gilts', Node([
                Link('sneezer', Node([
                    Field('flowers'),
                    Field('doozie'),
                    Link('pins', Node([
                        Field('gunya'),
                        Link('kilned', Node([
                            Field('rusk'),
                        ])),
                    ])),
                    Field('apres'),
                ]), options={'gire': 'noatak'}),
                Link('movies', Node([
                    Field('boree'),
                ])),
            ])),
        ]),
    )


def test_reference_cycle_in_fragments():
    with pytest.raises(TypeError) as err:
        read("""
        query Suckle {
          roguish
          ...Pakol
        }
        fragment Pakol on Crees {
          fatuous
          ...Varlet
        }
        fragment Varlet on Bribee {
          penfold
          ...Pakol
        }
        """)
    err.match('Cyclic fragment usage: "Pakol"')


def test_duplicated_fragment_names():
    with pytest.raises(TypeError) as err:
        read("""
        query Pelota {
          sinope
        }
        fragment Splosh on Makai {
          saggier
        }
        fragment Splosh on Whether {
          refits
        }
        """)
    err.match('Duplicated fragment name: "Splosh"')


def test_variables_in_query():
    check_read(
        """
        query Milks($barwin: String, $alpacas: Int = 123) {
          inlined(finn: $barwin, buccina: $alpacas)
        }
        """,
        Node([Field('inlined',
                    options={'finn': 'fanless', 'buccina': 123})]),
        {'barwin': 'fanless'},
    )


def test_variables_in_fragment():
    check_read(
        """
        query Jester($popedom: String, $tookies: Int = 234) {
          ...Pujari
        }

        fragment Pujari on Ashlee {
          inlined(bankit: $popedom, riuer: $tookies)
        }
        """,
        Node([Field('inlined',
                    options={'bankit': 'halle', 'riuer': 234})]),
        {'popedom': 'halle'},
    )


def test_undefined_variables():
    with pytest.raises(TypeError) as err:
        read("""
        {
          selma(djin: $geeky)
        }
        """)
    err.match('Variable \$geeky is not defined in query <unnamed>')

    with pytest.raises(TypeError) as err:
        read("""
        query Oriolus {
          ve(sac: $bd)
        }
        """)
    err.match('Variable \$bd is not defined in query Oriolus')

    with pytest.raises(TypeError) as err:
        read("""
        query Had {
          ...Fulgent
        }

        fragment Fulgent on Ashlee {
          chewie(newton: $aliyah)
        }
        """)
    err.match('Variable \$aliyah is not defined in query Had')


def test_missing_variables():
    with pytest.raises(TypeError) as err:
        read("""
        query Belinda($asides: Int) {
          ebonics
        }
        """)
    err.match('Variable "asides" is not provided for query Belinda')
