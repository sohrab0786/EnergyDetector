from django.shortcuts import redirect, render
import uuid











def coolroof(request):
    # # GENERATES UNIQUE CODE FOR WORKING DIRECTORY OF USER FOR A PARTICULAR SIMULATION
    # file_uuid = uuid.uuid1()
    # print(file_uuid)
    #
    # basecaser = basecase
    # basecasee = "0.87"
    # proposedcaser = proposedcase
    # proposedcasee = "0.87"
    #
    # if (basecase == "0.23"):
    #     basecasee = "0.87"
    #
    # elif (basecase == "0.22"):
    #     basecasee = "0.91"
    #
    # elif (basecase == "0.25"):
    #     basecasee = "0.90"
    #
    # elif (basecase == "0.33"):
    #     basecasee = "0.90"
    #
    # elif (basecase == "0.34"):
    #     basecasee = "0.90"
    #
    # elif (basecase == "0.61"):
    #     basecasee = "0.25"
    #
    # elif (basecase == "0.65"):
    #     basecasee = "0.90"
    #
    # elif (basecase == "0.67"):
    #     basecasee = "0.85"
    #
    # elif (basecase == "0.69"):
    #     basecasee = "0.87"
    #
    # elif (basecase == "0.73"):
    #     basecasee = "0.90"
    #
    # elif (basecase == "0.80"):
    #     basecasee = "0.91"
    #
    # elif (basecase == "0.83"):
    #     basecasee = "0.92"
    #
    # elif (basecase == "0.85"):
    #     basecasee = "0.91"
    #
    # if (proposedcase == "0.23"):
    #     proposedcasee = "0.87"
    #
    # elif (proposedcase == "0.22"):
    #     proposedcasee = "0.91"
    #
    # elif (proposedcase == "0.25"):
    #     proposedcasee = "0.90"
    #
    # elif (proposedcase == "0.33"):
    #     proposedcasee = "0.90"
    #
    # elif (proposedcase == "0.34"):
    #     proposedcasee = "0.90"
    #
    # elif (proposedcase == "0.61"):
    #     proposedcasee = "0.25"
    #
    # elif (proposedcase == "0.65"):
    #     proposedcasee = "0.90"
    #
    # elif (proposedcase == "0.67"):
    #     proposedcasee = "0.85"
    #
    # elif (proposedcase == "0.69"):
    #     proposedcasee = "0.87"
    #
    # elif (proposedcase == "0.73"):
    #     proposedcasee = "0.90"
    #
    # elif (proposedcase == "0.80"):
    #     proposedcasee = "0.91"
    #
    # elif (proposedcase == "0.83"):
    #     proposedcasee = "0.92"
    #
    # elif (proposedcase == "0.85"):
    #     proposedcasee = "0.91"
    #

    return render(request, "Coolroof.html")
