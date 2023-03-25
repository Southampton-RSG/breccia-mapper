import json
import os

from django.core.management.commands import loaddata

from bootstrap_customizer.models import BootstrapTheme


def should_add_record(record):
    if record['model'] != 'bootstrap_customizer.bootstraptheme':
        return True

    return not BootstrapTheme.objects.filter(
        pk=record['pk'],
    ).exists()


class Command(loaddata.Command):
    def handle(self, *args, **options):
        args = list(args)

        # Read the original JSON file
        file_name = args[0]
        with open(file_name) as json_file:
            json_list = json.load(json_file)

        # Filter out records that already exists
        json_list_filtered = list(filter(should_add_record, json_list))
        if not json_list_filtered:
            print("All data are already previously loaded")
            return

        # Write the updated JSON file
        file_dir_and_name, file_ext = os.path.splitext(file_name)
        file_name_temp = f"{file_dir_and_name}_temp{file_ext}"
        with open(file_name_temp, 'w') as json_file_temp:
            json.dump(json_list_filtered, json_file_temp)

        # Pass the request to the actual loaddata (parent functionality)
        args[0] = file_name_temp
        super().handle(*args, **options)

        # You can choose to not delete the file so that you can see what was added to your records
        os.remove(file_name_temp)
