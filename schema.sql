BEGIN TRANSACTION;
CREATE TABLE `files` (
	`id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	`filename`	TEXT NOT NULL,
	`fraud`	INTEGER NOT NULL,
	`loathing`	REAL NOT NULL
);
COMMIT;