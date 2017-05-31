from __future__ import unicode_literals

from django.db import models

# Create your models here.

class Project(models.Model):
    Name = models.TextField()
    URL = models.TextField()

class File(models.Model):
    Name = models.TextField()
    URL = models.TextField()
    ProjectName = models.ForeignKey(Project)
    FilePath = models.TextField()

class Bear(models.Model):
    Bear = models.TextField()
    ProjectName = models.ForeignKey(Project)
    FileName = models.ForeignKey(File)
    StartLine = models.IntegerField()
    StartLineURL = models.TextField()
    EndLine = models.IntegerField()
    EndLineURL = models.TextField()
    Aspect = models.TextField()
    Confidence = models.IntegerField()
    DebugMsg = models.TextField()
    Diffs = models.TextField()
    BearId = models.TextField()
    Message = models.TextField()
    MessageArguments = models.TextField()
    MessageBase = models.TextField()
    Severity = models.IntegerField()
