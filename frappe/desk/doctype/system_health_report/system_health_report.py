# Copyright (c) 2024, Frappe Technologies and contributors
# For license information, please see license.txt
"""
Basic system health check report to see how everything on site is functioning in one single page.

Metrics:
- [x] Background jobs, workers and scheduler summary, queue stats
- [ ] SocketIO works (using basic ping test)
- [ ] Email queue flush and pull
- [ ] Error logs status
- [ ] Database - storage usage and top tables, version
- [ ] Storage - files usage
- [ ] Backups
- [ ] Log cleanup status
- [ ] User - new users, sessions stats, failed login attempts
- [ ] Updates / Security updates ?




"""

from collections import defaultdict

import frappe
from frappe.model.document import Document
from frappe.utils.background_jobs import get_queue, get_queue_list
from frappe.utils.scheduler import get_scheduler_status


class SystemHealthReport(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.desk.doctype.system_health_queue.system_health_queue import SystemHealthQueue
		from frappe.desk.doctype.system_health_workers.system_health_workers import SystemHealthWorkers
		from frappe.types import DF

		background_workers: DF.Table[SystemHealthWorkers]
		queue_status: DF.Table[SystemHealthQueue]
		scheduler_status: DF.Data | None
		socketio_ping_check: DF.Literal["Fail", "Pass"]
		socketio_transport_mode: DF.Literal["Polling", "Websocket"]
		total_background_workers: DF.Int
	# end: auto-generated types

	def db_insert(self, *args, **kwargs):
		raise NotImplementedError

	def load_from_db(self):
		super(Document, self).__init__({})
		self.fetch_background_workers()

	def fetch_background_workers(self):
		self.scheduler_status = get_scheduler_status().get("status")
		workers = frappe.get_all("RQ Worker")
		self.total_background_workers = len(workers)
		queue_summary = defaultdict(list)

		for worker in workers:
			queue_summary[worker.queue_type].append(worker)

		for queue_type, workers in queue_summary.items():
			self.append(
				"background_workers",
				{
					"count": len(workers),
					"queues": queue_type,
					"failed_jobs": sum(w.failed_job_count for w in workers),
					"utilization": sum(w.utilization_percent for w in workers) / len(workers),
				},
			)

		for queue in get_queue_list():
			q = get_queue(queue)
			self.append(
				"queue_status",
				{
					"queue": queue,
					"pending_jobs": q.count,
				},
			)

	def db_update(self):
		raise NotImplementedError

	def delete(self):
		raise NotImplementedError

	@staticmethod
	def get_list(filters=None, page_length=20, **kwargs):
		raise NotImplementedError

	@staticmethod
	def get_count(filters=None, **kwargs):
		raise NotImplementedError

	@staticmethod
	def get_stats(**kwargs):
		raise NotImplementedError
