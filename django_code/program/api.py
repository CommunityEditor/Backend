from ourjseditor import api

import json
import datetime

from django.template.defaultfilters import escape

from models import Program
from views import key_func_mapping
from vote.models import vote_types
from notification.models import Notif

@api.standardAPIErrors("POST")
@api.login_required
def new_program(request):
    data = json.loads(request.body)
    if (len(data["title"]) > 45):
        return api.error("Title length exceeds maximum characters.")

    program = Program.objects.create(
        user = request.user,
        title = data["title"],
        html = data["html"],
        js = data["js"],
        css = data["css"],
    )

    response = api.succeed({"id": program.program_id}, status=201)
    response["Location"] = "/program/" + program.program_id
    return response

@api.standardAPIErrors("GET","PATCH","DELETE")
def program(request, program_id):
    requested_program = Program.objects.get(program_id=program_id)
    if (request.method == "GET"):
        return api.succeed(requested_program.to_dict())
    elif (request.method == "PATCH"):
        data = json.loads(request.body)
        return_data = {}

        if request.user != requested_program.user:
            return api.error("Not authorized.", status=401)

        valid_props = ["html", "js", "css", "title"]

        if "title" in data and len(data["title"]) > 45:
            return api.error("Title length exceeds maximum characters.", status=400)

        if "publishedMessage" in data and len(data["publishedMessage"]) > 250:
                return api.error("Publish message can't exceed 250 characters")

        for prop in valid_props:
            if prop in data:
                setattr(requested_program, prop, data[prop])

        if "publishedMessage" in data:
            requested_program.published_message = data["publishedMessage"];
            requested_program.last_published = datetime.datetime.now()

            return_data["lastPublished"] = requested_program.last_published.replace(microsecond=0).isoformat() + "Z"

            # Create notification for subscribers
            subscribers = requested_program.user.profile.profile_set.all()
            for subscriber in subscribers:
                Notif.objects.create(
                    target_user = subscriber.user,
                    link = "/program/" + requested_program.program_id,
                    description = "<strong>{0}</strong> just published a new program, <strong>{1}</strong>".format(
                        escape(request.user.profile.display_name), escape(requested_program.title)),
                    source_program = requested_program
                )

        requested_program.save()

        return api.succeed(return_data)
    elif (request.method == "DELETE"):
        if request.user != requested_program.user:
            return api.error("Not authorized.", status=401)

        requested_program.delete()

        return api.succeed()

@api.standardAPIErrors("GET")
def program_list(request, sort):
    if (not sort):
        sort = "new" # Default sort. sort is actually passed in as None, so we can't use an argument default

    if (sort not in key_func_mapping):
        return api.error("Invalid sort type: \"{}\"".format(sort))

    key_func = key_func_mapping[sort]
    if (type(key_func) is unicode):
        key_func = lambda program: getattr(program, key_func_mapping[sort])

    programs = sorted(Program.objects.all(), reverse=True, key=key_func)[:20]

    program_dicts = []
    for program in programs:
        program = program.to_dict()
        del(program["css"])
        del(program["html"])
        del(program["js"])
        program_dicts.append(program)

    return api.succeed({"sort": sort, "programs": program_dicts})
