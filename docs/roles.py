"""
Miscellaneous Sphinx roles based on `Defining Custom Roles in Sphinx
<http://www.doughellmann.com/articles/how-tos/sphinx-custom-roles/index.html`__
by Doug Hellmann.
"""
from docutils import nodes
from docutils.parsers.rst.roles import set_classes

def github_project_role(name, rawtext, text, lineno, inliner, options={}, content=[]):
    """
    Link to a GitHub account or project.

    Returns 2 part tuple containing list of nodes to insert into the
    document and a list of system messages.  Both are allowed to be
    empty.

    :param name: The role name used in the document.
    :param rawtext: The entire markup snippet, with role.
    :param text: The text marked with the role.
    :param lineno: The line number where rawtext appears in the input.
    :param inliner: The inliner instance that called us.
    :param options: Directive options for customization.
    :param content: The directive content for customization.
    """

    try:
        if '/' in text:
            (account, project) = text.strip().split('/')
        else:
            (account, project) = (text.strip(), None)

    except Exception:
        msg = inliner.reporter.error(
            'GitHub requires `account/project` or `account`; '
            '"%s" is invalid.' % text, line=lineno)
        prb = inliner.problematic(rawtext, rawtext, msg)
        return [prb], [msg]

    app = inliner.document.settings.env.app
    node = make_github_link_node(rawtext, app, account, project, options)
    return [node], []

def make_github_link_node(rawtext, app, account, project, options):
    """
    Create a link to a GitHub account or project.

    :param rawtext: Text being replaced with link node.
    :param app: Sphinx application context
    :param account: GitHub account name
    :param project: GitHub project name
    :param options: Options dictionary passed to role func.
    """
    base = app.config.github_url or 'https://github.com/'
    slash = '/' if base[-1] != '/' else ''

    pagename = account + '/' + (project if project else '')
    ref = base + slash + pagename

    set_classes(options)

    node = nodes.reference(rawtext, pagename, refuri=ref,
                           **options)
    return node

def pypi_project_role(name, rawtext, text, lineno, inliner, options={}, content=[]):
    """
    Link to a PyPI ("cheeseshop") project.

    Returns 2 part tuple containing list of nodes to insert into the
    document and a list of system messages.  Both are allowed to be
    empty.

    :param name: The role name used in the document.
    :param rawtext: The entire markup snippet, with role.
    :param text: The text marked with the role.
    :param lineno: The line number where rawtext appears in the input.
    :param inliner: The inliner instance that called us.
    :param options: Directive options for customization.
    :param content: The directive content for customization.
    """

    project = text.strip()

    app = inliner.document.settings.env.app
    node = make_pypi_link_node(rawtext, app, project, options)
    return [node], []

def make_pypi_link_node(rawtext, app, project, options):
    """
    Create a link to a PyPI ("cheeseshop") project.

    :param rawtext: Text being replaced with link node.
    :param app: Sphinx application context
    :param project: PyPI project name
    :param options: Options dictionary passed to role func.
    """
    base = app.config.pypi_url or 'http://pypi.python.org/pypi/'
    slash = '/' if base[-1] != '/' else ''

    ref = base + slash + project

    set_classes(options)

    node = nodes.reference(rawtext, project, refuri=ref,
                           **options)
    return node

def wikipedia_role(name, rawtext, text, lineno, inliner, options={}, content=[]):
    """
    Link to a Wikipedia article.

    Returns 2 part tuple containing list of nodes to insert into the
    document and a list of system messages.  Both are allowed to be
    empty.

    :param name: The role name used in the document.
    :param rawtext: The entire markup snippet, with role.
    :param text: The text marked with the role.
    :param lineno: The line number where rawtext appears in the input.
    :param inliner: The inliner instance that called us.
    :param options: Directive options for customization.
    :param content: The directive content for customization.
    """

    article = text.strip()
    if not article:
        msg = inliner.reporter.error(
            'Wikipedia requires an `article name`; '
            '"%s" is invalid.' % text, line=lineno)
        prb = inliner.problematic(rawtext, rawtext, msg)
        return [prb], [msg]

    app = inliner.document.settings.env.app
    node = make_wikipedia_link_node(rawtext, app, article, options)
    return [node], []

def make_wikipedia_link_node(rawtext, app, article, options):
    """
    Create a link to a Wikipedia article

    :param rawtext: Text being replaced with link node.
    :param app: Sphinx application context
    :param account: GitHub account name
    :param project: GitHub project name
    :param options: Options dictionary passed to role func.
    """
    base = app.config.wikipedia_url % app.config.wikipedia_lang
    slash = '/' if base[-1] != '/' else ''

    # sugar: wiki-ize the article name (somewhat...)
    article_page = (article[0].upper() + article[1:].lower()).replace(' ', '_')

    ref = base + slash + article_page

    set_classes(options)

    node = nodes.reference(rawtext, article, refuri=ref,
                           **options)
    return node

def setup (app):
    """
    Install the plugins.

    :param app: Sphinx application context.
    """
    app.add_role('github', github_project_role)
    app.add_config_value('github_url', None, 'env')

    app.add_role('pypi', pypi_project_role)
    app.add_config_value('pypi_url', None, 'env')

    app.add_role('wikipedia', wikipedia_role)
    app.add_config_value('wikipedia_url', 'http://%s.wikipedia.org/wiki/', 'env')
    app.add_config_value('wikipedia_lang', 'en', 'env')
