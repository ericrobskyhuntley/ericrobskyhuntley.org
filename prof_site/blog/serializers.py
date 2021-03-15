from rest_framework import serializers
from .models import Education, Institution, Committee_Membership, Person, Affiliation, Award

class InstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        depth = 6
        model = Institution
        exclude = ['id']

class AffiliationSerializer(serializers.ModelSerializer):
    start = serializers.DateField(format='%Y')
    end = serializers.DateField(format='%Y')
    institution = InstitutionSerializer()
    class Meta:
        model = Affiliation
        exclude = ['id', 'primary', 'kind', 'show', 'person']

class MainPersonSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField()
    pronouns = serializers.CharField(source='get_pronouns_display')
    cred = serializers.CharField(source='get_cred_display')
    class Meta:
        depth = 6
        model = Person
        exclude = ['id', 'page', 'main', 'affil', 'first', 'middle', 'last']

class CommitteeSerializer(serializers.ModelSerializer):
    chair = serializers.ReadOnlyField()
    name = serializers.ReadOnlyField(source='full_name')
    website = serializers.ReadOnlyField()
    email = serializers.ReadOnlyField()
    cred = serializers.ReadOnlyField(source='get_cred_display')
    class Meta:
        model = Committee_Membership
        fields = ['chair', 'name', 'website', 'email', 'cred']

class EducationSerializer(serializers.ModelSerializer):
    start = serializers.DateField(format='%Y')
    end = serializers.DateField(format='%Y')
    institution = InstitutionSerializer()
    committee = CommitteeSerializer(many=True)
    degree = serializers.ReadOnlyField(source='get_degree_display')

    class Meta:
        model = Education
        exclude = ['terminal', 'show', 'id']

class AwardSerializer(serializers.ModelSerializer):
    grantor = InstitutionSerializer()
    grantees = InstitutionSerializer(many=True)
    start = serializers.DateField(format='%Y')
    end = serializers.DateField(format='%Y')
    class Meta:
        model = Award
        exclude = ['id', 'show', 'kind']