from django.db import models


from people import models as people_models


class ActivityType(models.Model):
    """
    Representation of the type of activity being conducted.

    Examples may include: 'research activity' or 'stakeholder engagement'.
    """
    #: Name of this type of activity
    name = models.CharField(max_length=255,
                            unique=True,
                            blank=False, null=False)
    
    def __str__(self) -> str:
        return self.name
    

class ActivityMedium(models.Model):
    """
    Representation of the medium via which the activity is conducted.

    Examples may include: 'face to face' or 'virtual'.
    """
    #: Name of this medium
    name = models.CharField(max_length=255,
                            unique=True,
                            blank=False, null=False)

    def __str__(self) -> str:
        return self.name


class ActivitySeries(models.Model):
    """
    A series of related :class:`Activity`s.
    """
    class Meta:
        verbose_name_plural = 'activity series'

    #: Name of activity series
    name = models.CharField(max_length=1023,
                            blank=False, null=False)

    #: What type of activity does this series represent?
    type = models.ForeignKey(ActivityType,
                             on_delete=models.PROTECT,
                             blank=False, null=False)

    #: How are activities in this series typically conducted?
    medium = models.ForeignKey(ActivityMedium,
                               on_delete=models.PROTECT,
                               blank=False, null=False)

    def __str__(self) -> str:
        return self.name


class Activity(models.Model):
    """
    An instance of an activity - e.g. a workshop.
    """
    class Meta:
        verbose_name_plural = 'activities'

    #: Name of activity
    name = models.CharField(max_length=1023,
                            blank=False, null=False)

    #: Optional :class:`ActivitySeries` to which this activity belongs
    series = models.ForeignKey(ActivitySeries,
                               related_name='activities',
                               on_delete=models.PROTECT,
                               blank=True, null=True)

    #: What type of activity is this?
    type = models.ForeignKey(ActivityType,
                             on_delete=models.PROTECT,
                             blank=False, null=False)

    #: How was this activity conducted?
    medium = models.ForeignKey(ActivityMedium,
                               on_delete=models.PROTECT,
                               blank=False, null=False)
    
    #: Who attended this activity?
    attendance_list = models.ManyToManyField(people_models.Person,
                                             related_name='activities')

    def __str__(self) -> str:
        return self.name
