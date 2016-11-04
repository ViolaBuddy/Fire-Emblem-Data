USE FireEmblemData;

# The number of characters who can use each weapon type
SELECT WeaponType, COUNT(DISTINCT CharId) AS NumberOfCharacters FROM
	(SELECT R.CharId, CP.PromotedClass as ClassName
	FROM Reclasses R, ClassPromotions CP
	WHERE R.BaseClassName = CP.BaseClass
	UNION
	SELECT CharId, BaseClassName as ClassName
	FROM Reclasses R
	ORDER BY CharId ASC, ClassName ASC) R,
    ClassWeapons CW WHERE
R.ClassName = CW.ClassName GROUP BY CW.WeaponType ORDER BY Count(DISTINCT CharId) DESC;