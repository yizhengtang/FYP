from gmail_api import initialize_gmail_service, create_label, list_labels, modify_labels, delete_label, get_label_details

service = initialize_gmail_service()

labels = ['Course', 'Personal']
course_labels = ['CICD', 'FYP', 'Mobile App Development']
created_labels = []

for label in labels:
    try:
        label = create_label(service, label)
        print(f"Label '{label['name']}' created with ID: {label['id']}")
        created_labels.append(label)

        if label['name'] == 'Course':
            for course_label in course_labels:
                try:
                    sub_label = create_label(service, f'{label["name"]}/{course_label}')
                    print(f" Sub-label '{label['name']}/{course_label}' created with ID: {sub_label['id']}")
                    created_labels.append(sub_label)
                except Exception as e:
                    print(f" Failed to create sub-label '{course_label}': {e}")
    except Exception as e:
        print(f"Failed to create label '{label}': {e}")

gmail_labels = list_labels(service)
for label in gmail_labels:
    print(f"Label Name: {label['name']}")
    print(f"Label ID: {label['id']}")

