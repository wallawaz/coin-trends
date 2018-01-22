import flask
from flask import g, jsonify
from time import sleep


def create_app(sa):

    app = flask.Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
    )

    @app.errorhandler(404)
    def page_not_found(error):
        return flask.render_template("404.html")

    @app.errorhandler(500)
    def interval_server_error(error):
        return flask.render_template("500.html")
    
    @app.route("/top_icos")
    def top_icos():
        """
        (last_post, thread_id, subject, post_count)
        """
        results = sa.get_top_ico_threads()

        output = {"top_icos": []}
        for result in results:

            ts, thread_id, subject, post_count = result
            output["top_icos"].append({
                "last_post": str(ts),
                "thread_id": thread_id,
                "subject": subject,
                "post_count": post_count,
            })

        return jsonify(output)

    @app.route("/posts_by_thread/<int:thread_id>")
    def posts_by_thread(thread_id):
        results = sa.get_posts_by_thread(thread_id)
        columns = ["post_id", "created_at", "comment"]
        output = {"columns": columns, "rows": []}

        for result in results:
            d = dict.fromkeys(columns)
            for i, value in enumerate(result):
                d[columns[i]] = value
            output["rows"].append(d)

        return jsonify(output)

    @app.route("/")
    def index():
        return flask.render_template("dev.html")
    
    return app