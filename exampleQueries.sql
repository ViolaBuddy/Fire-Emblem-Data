USE FireEmblemData;

# Characters and all their reclasses, not just their base class
SELECT R.CharId, CP.PromotedClass as ClassName
FROM Reclasses R, ClassPromotions CP
WHERE R.BaseClassName = CP.BaseClass
UNION
SELECT CharId, BaseClassName as ClassName
FROM Reclasses R
ORDER BY CharId ASC, ClassName ASC;

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






### The following works in theory cannot be represented with a native MYSQL DOUBLE, which
### is what POW returns.

DELIMITER $$
DROP FUNCTION IF EXISTS `Fact`$$
CREATE FUNCTION `Fact`(`N` DECIMAL(50,30)) RETURNS DECIMAL(50,30)
BEGIN
	DECLARE acc DECIMAL(50,30) DEFAULT 1;
    DECLARE i DECIMAL(50,30) DEFAULT N;
	label1: LOOP
		IF i <= 0 THEN
			RETURN acc;
		END IF;
		SET acc = acc * i;
		SET i = i - 1;
	END LOOP label1;
END$$
DROP FUNCTION IF EXISTS `NChooseK2`$$
CREATE FUNCTION `NChooseK2`(`N` DECIMAL(50,30), `K` DECIMAL(50,30)) RETURNS DECIMAL(50,30)
BEGIN
	IF K > N THEN
		RETURN 0;
	END IF;
	RETURN (Fact(N)/Fact(K)/Fact(N-K));
END$$
DROP FUNCTION IF EXISTS `NChooseK`$$
CREATE FUNCTION `NChooseK`(`N` DECIMAL(50,30), `K` DECIMAL(50,30)) RETURNS DECIMAL(50,30)
BEGIN
	IF K > N THEN
		RETURN 0;
	END IF;

	DECLARE temp DECIMAL(50, 30);
	DECLARE acc DECIMAL(50, 30);

	SET temp = K;
	SET acc = 1;
	label1: LOOP
		IF temp > N THEN
			RETURN 
	END LOOP label1;
	RETURN acc/Fact(N-K));
END$$


# the probability of having M level ups with a stat increase
# given N_u unpromoted level ups and N_p promoted level ups
# where u and p are percentage chances of increasing in the given
# in unpromoted and promoted classes, respectively
DELIMITER $$
DROP FUNCTION IF EXISTS `AtLeastMLevelUps`$$
CREATE FUNCTION `AtLeastMLevelUps`(`M` DECIMAL(50,30), `N_u` DECIMAL(50,30), `N_p` DECIMAL(50,30), `u` DECIMAL(50,30), `p` DECIMAL(50,30)) RETURNS DECIMAL(65,30)
BEGIN
	# Sum over m=0..M of (Sum over k=m..N_u of (N_u choose k) (1-u)^(N_u-k) u^k + Sum over k=(M-m)..N_p of (N_p choose k) (1-p)^(N_p-k) p^k)
	DECLARE m_small DECIMAL(65,30) DEFAULT 0;
    DECLARE k DECIMAL(65,30) DEFAULT 0;
    DECLARE result1 DECIMAL(65,30) DEFAULT 0;
    DECLARE result2 DECIMAL(65,30) DEFAULT 0;
    DECLARE overallresult DECIMAL(65,30) DEFAULT 0;

    SET m_small = 0;
	outerloop: LOOP
		# probability of exactly m_small level ups while unpromoted:
		SET result1 = NChooseK(N_u, m_small) * POWER(1 - (u/100), N_u - m_small) * POWER(u/100, m_small);

		SET result2 = 0;
		SET k = M - m_small;
		innerloop1: LOOP
			IF k <= 0 THEN
				# We've already reached M or more within the unpromoted levels
				SET result2 = 1;
				LEAVE innerloop1;
			END IF;
			SET result2 = result2 + NChooseK(N_p, k) * POWER(1 - (p/100), N_p - k) * POWER(p/100, k);

			SET k = k + 1;
			IF k > N_p THEN
				LEAVE innerloop1;
			END IF;
		END LOOP innerloop1;

		SET overallresult = overallresult + result1*result2;

		SET m_small = m_small+1;
		IF m_small > N_u THEN
			LEAVE outerloop;
		END IF;
	END LOOP outerloop;

	RETURN overallresult;
END
$$
SELECT AtLeastMLevelUps(1, 1, 20, 50, 0)
$$





SELECT
	Ch.CharId, CBS.BaseLck AS 'Luck Character Base',CBS.BaseLevel,
	
	Cl1.ClassName AS 'Unpromoted Class Name',
	19 - CBS.BaseLevel AS 'Level Ups Left (Unpromoted Class)',
	Cl1.MaxLck+Ch.ModifierMaxLck AS 'Luck Cap (Unpromoted Class)',
	Cl1.BaseLck - ClBase.BaseLck + CBS.BaseLck AS 'Luck Base (Unpromoted Class)',
	Cl1.GrowthLck+Ch.GrowthLck AS 'Luck Growth (Unpromoted Class)',
	(Cl1.BaseLck - ClBase.BaseLck + CBS.BaseLck) + (Cl1.GrowthLck+Ch.GrowthLck) * (19 - CBS.BaseLevel) / 100  AS 'Average Level 20 Luck (Unpromoted Class)',

	Cl2.ClassName AS 'Promoted Class Name',
	19 AS 'Level Ups Left (Promoted Class)',
	Cl2.MaxLck+Ch.ModifierMaxLck AS 'Luck Cap (Promoted Class)',
	Cl2.BaseLck - ClBase.BaseLck + CBS.BaseLck AS 'Luck Base (Promoted Class)',
	Cl2.GrowthLck+Ch.GrowthLck AS 'Luck Growth (Promoted Class)',
	(Cl1.BaseLck - ClBase.BaseLck + CBS.BaseLck) + (Cl1.GrowthLck+Ch.GrowthLck) * (19 - CBS.BaseLevel) / 100 +
	 (Cl2.BaseLck - ClBase.BaseLck + CBS.BaseLck) + (Cl2.GrowthLck+Ch.GrowthLck) * (19) / 100  AS 'Average Level 20 Luck (Promoted Class)'

FROM classstats AS Cl1,
	classstats AS Cl2,
	classstats AS ClBase,
	characterstats AS Ch,
	characterbasestats AS CBS,
	classpromotions AS CP

WHERE Ch.CharId = CBS.CharId AND CBS.CharId = 'Arthur' AND 

Cl1.ClassName = CP.BaseClass AND
Cl2.ClassName = CP.PromotedClass AND
ClBase.ClassName = CBS.Class

AND (Cl2.MaxLck+Ch.ModifierMaxLck) > (Cl2.BaseLck - ClBase.BaseLck + CBS.BaseLck) + (39 - CBS.BaseLevel) #Filter out where reaching the cap is impossible

ORDER BY `Average Level 20 Luck (Promoted Class)` DESC, `Luck Cap (Promoted Class)` ASC;