from django.db import models


class Employee(models.Model):
    """Registered employees with face photo."""
    user_id    = models.CharField(max_length=50, unique=True)
    user_name  = models.CharField(max_length=100)
    email      = models.EmailField(unique=True)
    face_image = models.ImageField(upload_to='employees/')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'employee'

    def _str_(self):
        return f"{self.user_name} ({self.user_id})"


class Attendance(models.Model):
    """Attendance records for each employee."""
    user_id        = models.CharField(max_length=50)
    user_name      = models.CharField(max_length=100)
    date           = models.DateField()

    checkin_time   = models.DateTimeField(null=True, blank=True)
    checkin_lat    = models.FloatField(null=True, blank=True)
    checkin_lng    = models.FloatField(null=True, blank=True)
    checkin_image  = models.ImageField(upload_to='selfies/', null=True, blank=True)

    checkout_time  = models.DateTimeField(null=True, blank=True)
    checkout_lat   = models.FloatField(null=True, blank=True)
    checkout_lng   = models.FloatField(null=True, blank=True)
    checkout_image = models.ImageField(upload_to='selfies/', null=True, blank=True)

    face_verified  = models.BooleanField(default=False)

    class Meta:
        db_table = 'attendance'
        ordering = ['-date', '-checkin_time']

    def _str_(self):
        return f"{self.user_name} ({self.user_id}) – {self.date}"

    @property
    def duration(self):
        if self.checkin_time and self.checkout_time:
            diff  = self.checkout_time - self.checkin_time
            total = int(diff.total_seconds())
            h, m  = divmod(total // 60, 60)
            return f"{h}h {m}m"
        return None