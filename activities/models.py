from django.db import models


class ActivitySeries(models.Model):
    """
    A series of related :class:`Activity`s
    """

    class Meta:
        verbose_name_plural = 'activity series'

    #: Name of activity series
    name = models.CharField(max_length=1023,
                            blank=False, null=False)

    def __str__(self) -> str:
        return self.name


class Activity(models.Model):
    """
    An instance of an activity - e.g. a workshop
    """

    class Meta:
        verbose_name_plural = 'activities'

    #: Name of activity
    name = models.CharField(max_length=1023,
                            blank=False, null=False)

    #: Optional :class:`ActivitySeries` to which this activity belongs
    series = models.ForeignKey(ActivitySeries, related_name='instances',
                               on_delete=models.PROTECT,
                               blank=True, null=True)

    def __str__(self) -> str:
        return self.name
