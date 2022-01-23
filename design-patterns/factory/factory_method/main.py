from concrete_creator import Linkedin, Facebook

profile_type = input(
    "Which Profile youd like'd to create? [linkedin or facebook]")
print(f"Creating Profile.. {profile_type}")


if profile_type == 'facebook':
    facebook = Facebook()
    print('Profile has sections --', facebook.get_sections())
elif profile_type == 'linkedin':
    linkedin = Linkedin()
    print('Profile has sections --', linkedin.get_sections())